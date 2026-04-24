from dataclasses import dataclass

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.db import get_db
from backend.logger import logger
from backend.services.auth_service import decode_token
from backend.services.crypto_service import CryptoService
from backend.settings import get_settings
from backend.utils import mask_pii

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


@dataclass
class UserPrincipal:
    """Lightweight user identity for auth checks."""
    id: str
    role: str


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db=Depends(get_db)) -> UserPrincipal:
    """
    Dependency to get the authenticated user.
    Validates JWT and checks if user is still active in DB.
    """
    logger.debug(f"Validating token: {token[:10]}...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        typ: str = payload.get("typ")
        logger.debug(
            f"Payload decoded. sub: {mask_pii(user_id)}, role: {role}, typ: {typ}"
        )

        if user_id is None or typ != "access":
            logger.warning(f"Invalid token payload. sub={user_id}, typ={typ}")
            raise credentials_exception

    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

    # Check DB for active status
    try:
        logger.debug(f"Looking up user in DB: {mask_pii(user_id)}")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        logger.debug(f"ObjectId lookup failed, trying string: {e}")
        user = await db.users.find_one({"_id": user_id})

    if user is None:
        logger.warning(f"User not found in DB for id: {mask_pii(user_id)}")
        raise credentials_exception

    # Decrypt is_active from Binary status
    is_active = await CryptoService.decrypt_field(user["is_active"])
    if not is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User account is deactivated")

    return UserPrincipal(id=user_id, role=role)


async def require_admin(current_user: UserPrincipal = Depends(
    get_current_user)) -> UserPrincipal:
    """Dependency to enforce admin-only access."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin privileges required")
    return current_user
