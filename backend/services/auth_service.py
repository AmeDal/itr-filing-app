import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from backend.logger import logger
from backend.services.token_blocklist import block_token, is_blocked
from backend.settings import get_settings

settings = get_settings()


def create_access_token(user_id: str, role: str) -> str:
    """Creates a short-lived access JWT."""
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": user_id,
        "role": role,
        "typ": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4())
    }

    return jwt.encode(to_encode,
                      settings.jwt_secret,
                      algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Creates a long-lived refresh JWT."""
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": user_id,
        "typ": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4())
    }

    return jwt.encode(to_encode,
                      settings.jwt_secret,
                      algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT.
    Raises jwt.PyJWTError if invalid.
    """
    payload = jwt.decode(token,
                         settings.jwt_secret,
                         algorithms=[settings.jwt_algorithm])

    # Check blocklist
    jti = payload.get("jti")
    if jti and is_blocked(jti):
        raise jwt.InvalidTokenError("Token has been revoked")

    return payload


def revoke_token(token: str):
    """Adds a token's JTI to the blocklist."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}  # Allow blocking even if expired
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            block_token(jti, exp)
    except jwt.PyJWTError as e:
        logger.debug(f"Could not decode token for revocation: {e}")
