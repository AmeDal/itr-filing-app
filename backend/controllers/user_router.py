import logging

from fastapi import APIRouter, HTTPException

from backend.schemas.user_schema import UserCreateRequest, UserLoginRequest, UserResponse
from backend.services import user_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/users", tags=["Users"])


@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(req: UserCreateRequest):
    """
    Creates a new user profile.
    """
    try:
        return await user_service.create_user(req)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception:
        logger.exception("Signup failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=UserResponse)
async def login(req: UserLoginRequest):
    """
    Authenticates a user via PAN and Password.
    """
    logger.info(f"Login attempt for PAN: {req.pan_number}")

    user = await user_service.login_user(req)
    if not user:
        logger.warning(f"Failed login for PAN: {req.pan_number}")
        raise HTTPException(status_code=401, detail="Invalid PAN or Password")

    logger.info(f"Successful login for PAN: {req.pan_number}")
    return user
