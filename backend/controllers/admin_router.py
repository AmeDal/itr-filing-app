import time
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, field_validator

from backend.auth_deps import UserPrincipal, oauth2_scheme, require_admin
from backend.db import get_db
from backend.logger import logger
from backend.security import async_hash_password, validate_password_strength
from backend.services import user_service
from backend.services.auth_service import revoke_token
from backend.services.crypto_service import CryptoService
from backend.services.user_deletion_service import bulk_hard_delete_users, hard_delete_user
from backend.settings import get_settings

router = APIRouter(prefix="/v1/admin", tags=["Admin"])


class AdminUserListResponse(BaseModel):
    users: List[dict]
    total: int
    skip: int
    limit: int


class RoleChangeRequest(BaseModel):
    role: str  # "admin" | "user"


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(
        ...,
        min_length=12,
        description=
        "New password must be at least 12 chars and contain uppercase, lowercase, number, and special char."
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        is_valid, err = validate_password_strength(v)
        if not is_valid:
            raise ValueError(err)
        return v


class BulkDeleteRequest(BaseModel):
    user_ids: List[str]


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(skip: int = Query(0, ge=0),
                     limit: int = Query(20, ge=1, le=100),
                     db=Depends(get_db),
                     _: UserPrincipal = Depends(require_admin)):
    """
    Returns a paginated list of all users with decrypted PII.
    """
    cursor = db.users.find({}).skip(skip).limit(limit)
    total = await db.users.count_documents({})

    users = []
    async for doc in cursor:
        # Decrypt all fields for admin (don't skip PII)
        decrypted = await user_service.decrypt_user_doc(
            doc, skip_fields={"password"})
        # Convert ObjectId to string for Pydantic serialization
        if "_id" in decrypted:
            decrypted["_id"] = str(decrypted["_id"])
        # Remove binary blobs that can't be JSON serialized
        decrypted.pop("password", None)
        # Convert encrypted booleans back from int (1/0)
        if "is_active" in decrypted:
            decrypted["is_active"] = bool(decrypted["is_active"])
        users.append(decrypted)

    return AdminUserListResponse(users=users,
                                 total=total,
                                 skip=skip,
                                 limit=limit)


@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    req: RoleChangeRequest,
    db=Depends(get_db),
    current_admin: UserPrincipal = Depends(require_admin)):
    """
    Changes a user's role. Implements last-admin guard.
    """
    if req.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Last admin guard
    if req.role == "user":
        enc_admin = await CryptoService.encrypt_deterministic("admin")
        enc_active = await CryptoService.encrypt_deterministic(True)
        admin_count = await db.users.count_documents({
            "role": enc_admin,
            "is_active": enc_active
        })
        target_user = await db.users.find_one({"_id": user_id})
        if target_user:
            # Check target role (must decrypt to check)
            dec_role = await CryptoService.decrypt_field(
                target_user.get("role"))
            if dec_role == "admin" and admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot demote the last active admin")

    result = await db.users.update_one({"_id": user_id}, {
        "$set": {
            "role": await CryptoService.encrypt_deterministic(req.role)
        }
    })

    if result.modified_count == 0:
        raise HTTPException(status_code=404,
                            detail="User not found or role unchanged")

    return {"detail": f"Role updated to {req.role}"}


@router.patch("/users/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    is_active: bool,
    db=Depends(get_db),
    current_admin: UserPrincipal = Depends(require_admin)):
    """
    Activates or deactivates a user account.
    """
    if not is_active:
        # Prevent self-deactivation or last admin deactivation
        if user_id == current_admin.id:
            raise HTTPException(status_code=400,
                                detail="Cannot deactivate yourself")

        enc_admin = await CryptoService.encrypt_deterministic("admin")
        enc_active = await CryptoService.encrypt_deterministic(True)
        admin_count = await db.users.count_documents({
            "role": enc_admin,
            "is_active": enc_active
        })
        target_user = await db.users.find_one({"_id": user_id})
        if target_user:
            dec_role = await CryptoService.decrypt_field(
                target_user.get("role"))
            if dec_role == "admin" and admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot deactivate the last active admin")

    await db.users.update_one({"_id": user_id}, {
        "$set": {
            "is_active": await CryptoService.encrypt_deterministic(is_active)
        }
    })
    return {
        "detail": f"User status set to {'active' if is_active else 'inactive'}"
    }


@router.delete("/users/{user_id}")
async def delete_user(user_id: str,
                      db=Depends(get_db),
                      current_admin: UserPrincipal = Depends(require_admin)):
    """
    Cascade hard-deletes a user. Cannot delete self.
    """
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # Last admin guard
    enc_admin = await CryptoService.encrypt_deterministic("admin")
    enc_active = await CryptoService.encrypt_deterministic(True)
    admin_count = await db.users.count_documents({
        "role": enc_admin,
        "is_active": enc_active
    })
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        user_oid = user_id

    target_user = await db.users.find_one({"_id": user_oid})
    if target_user:
        dec_role = await CryptoService.decrypt_field(target_user.get("role"))
        if dec_role == "admin" and admin_count <= 1:
            raise HTTPException(status_code=400,
                                detail="Cannot delete the last active admin")

    action_id = int(time.time())
    logger.info(
        f"[DELETE_ACTION_{action_id}] Request to delete user: {user_id}")

    res = await hard_delete_user(user_id)

    if not res.get("profile_deleted"):
        logger.warning(
            f"[DELETE_ACTION_{action_id}] FAILED: User {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=
            f"User {user_id} not found or already deleted. (ID: {action_id})")

    logger.info(
        f"[DELETE_ACTION_{action_id}] SUCCESS: User {user_id} deleted.")
    return res


@router.post("/users/bulk-delete")
async def bulk_delete_users_handler(
    req: BulkDeleteRequest,
    current_admin: UserPrincipal = Depends(require_admin)):
    """
    Bulk deletes users. Protects against self-deletion.
    """
    if current_admin.id in req.user_ids:
        # Filter out self
        req.user_ids = [uid for uid in req.user_ids if uid != current_admin.id]

    if not req.user_ids:
        raise HTTPException(
            status_code=400,
            detail=
            "No valid user IDs providing for deletion (cannot delete yourself)"
        )

    return await bulk_hard_delete_users(req.user_ids)


@router.post("/users/{user_id}/reset-password")
async def force_reset_password(
    user_id: str,
    req: ResetPasswordRequest,
    response: Response,
    db=Depends(get_db),
    token: str = Depends(oauth2_scheme),
    refresh_token: Optional[str] = Cookie(None),
    current_admin: UserPrincipal = Depends(require_admin)):
    """
    Forces a password reset for a user.
    """
    hashed_pwd = await async_hash_password(req.new_password)
    encrypted_pwd = await CryptoService.encrypt_random(hashed_pwd)

    try:
        user_oid = ObjectId(user_id)
    except Exception:
        user_oid = user_id

    result = await db.users.update_one({"_id": user_oid},
                                       {"$set": {
                                           "password": encrypted_pwd
                                       }})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Security: Revoke current session if it's a self-reset
    if user_id == current_admin.id:
        logger.info(
            f"Self-reset detected for admin {user_id}. Revoking tokens and cookies."
        )
        # 1. Revoke Access Token
        revoke_token(token)
        # 2. Revoke Refresh Token
        if refresh_token:
            revoke_token(refresh_token)
        # 3. Clear Cookie
        sets = get_settings()
        response.delete_cookie(key="refresh_token",
                               path=sets.refresh_token_cookie_path,
                               httponly=True,
                               secure=not sets.debug,
                               samesite="strict" if not sets.debug else "lax")

    return {"detail": "Password reset successful"}
