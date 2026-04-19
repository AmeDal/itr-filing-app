import logging
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Response, Cookie, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.schemas.user_schema import (UserCreateRequest, UserLoginRequest,
                                         UserResponse, UserSummary,
                                         AuthResponse, TokenRefreshResponse)
from backend.services import user_service
from backend.services.auth_service import (create_access_token,
                                           create_refresh_token, decode_token,
                                           revoke_token)
from backend.auth_deps import get_current_user, UserPrincipal, oauth2_scheme
from backend.settings import get_settings
from backend.utils import mask_pii, mask_email

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/v1/users", tags=["Users"])


@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(req: UserCreateRequest):
    """
    Creates a new user profile.
    """
    logger.info(f"Signup attempt for email: {mask_email(req.email)}")
    try:
        user = await user_service.create_user(req)
        logger.info(
            f"Signup success for: {mask_email(user.email)} (ID: {mask_pii(user.id)})"
        )
        return user
    except ValueError as e:
        logger.warning(
            f"Signup validation error for {mask_email(req.email)}: {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception:
        logger.exception(f"Unexpected signup failure for {mask_email(req.email)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=AuthResponse, include_in_schema=False)
async def login(response: Response,
                form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Universal login handler using standard OAuth2 form data.
    """
    try:
        pan = form_data.username.strip().upper()
        password = form_data.password

        # Reuse service logic
        login_req = UserLoginRequest(pan_number=pan, password=password)
        user = await user_service.login_user(login_req)

        if not user:
            logger.warning(f"Login failed for PAN: {mask_pii(pan)}")
            raise HTTPException(status_code=401,
                                detail="Invalid PAN or Password")

        if not user.is_active:
            logger.warning(f"Deactivated user login attempt: {mask_pii(pan)}")
            raise HTTPException(status_code=403,
                                detail="Account is deactivated")

        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        # Secure cookies for refresh token
        response.set_cookie(key="refresh_token",
                            value=refresh_token,
                            httponly=True,
                            secure=not settings.debug,
                            samesite="strict" if not settings.debug else "lax",
                            path=settings.refresh_token_cookie_path,
                            max_age=settings.refresh_token_expire_days * 24 *
                            60 * 60)

        user_summary = UserSummary.model_validate(user).model_dump()
        logger.debug(f"UserSummary generated: {user_summary}")

        res_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": user_summary
        }
        logger.info(f"Login success for: {mask_pii(pan)}. Returning result dict.")
        return res_data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during login handler")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh(response: Response,
                  refresh_token: Annotated[Optional[str],
                                           Cookie()] = None):
    """
    Rotates the access and refresh tokens using the refresh cookie.
    """
    logger.debug("Token refresh attempt")
    if not refresh_token:
        logger.warning("Refresh attempt missing cookie")
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = decode_token(refresh_token)
        if payload.get("typ") != "refresh":
            logger.warning("Invalid token type provided for refresh")
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        # Ensure user still exists and is active
        user = await user_service.get_user_by_oid(user_id)
        if not user or not user.is_active:
            logger.warning(
                f"Refresh failed: User {mask_pii(user_id)} is inactive or deleted"
            )
            raise HTTPException(status_code=401,
                                detail="User unavailable or inactive")

        # Rotate tokens
        revoke_token(refresh_token)  # Block current refresh token
        new_access = create_access_token(user.id, user.role)
        new_refresh = create_refresh_token(user.id)

        response.set_cookie(key="refresh_token",
                            value=new_refresh,
                            httponly=True,
                            secure=not settings.debug,
                            samesite="strict" if not settings.debug else "lax",
                            path=settings.refresh_token_cookie_path,
                            max_age=settings.refresh_token_expire_days * 24 *
                            60 * 60)

        logger.info(f"Tokens successfully rotated for user: {mask_pii(user_id)}")
        return TokenRefreshResponse(
            access_token=new_access,
            expires_in=settings.access_token_expire_minutes * 60)
    except Exception as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=401,
                            detail="Invalid or expired refresh token")


@router.post("/logout")
async def logout(response: Response,
                 token: str = Depends(oauth2_scheme),
                 current_user: UserPrincipal = Depends(get_current_user),
                 refresh_token: Annotated[Optional[str],
                                          Cookie()] = None):
    """
    Revokes both access and refresh tokens and clears the cookie.
    """
    logger.debug(f"Logout initiated for user: {mask_pii(current_user.id)}")
    if refresh_token:
        revoke_token(refresh_token)

    # Revoke the access token as well
    revoke_token(token)

    response.delete_cookie(key="refresh_token",
                           path=settings.refresh_token_cookie_path,
                           httponly=True,
                           secure=not settings.debug,
                           samesite="strict" if not settings.debug else "lax")
    logger.info(f"User logged out: {mask_pii(current_user.id)}")
    return {"detail": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserPrincipal = Depends(get_current_user)):
    """
    Returns the current authenticated user's profile.
    """
    logger.debug(f"Profile access for user: {mask_pii(current_user.id)}")
    user = await user_service.get_user_by_oid(current_user.id)
    if not user:
        logger.warning(
            f"Profile not found for authenticated ID: {mask_pii(current_user.id)}"
        )
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Profile retrieved for: {mask_email(user.email)}")
    return user
