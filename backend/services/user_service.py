import logging
from typing import Optional

from bson import ObjectId

from backend.db import DatabaseManager, generate_oid
from backend.schemas.user_schema import UserCreateRequest, UserLoginRequest, UserResponse
from backend.security import hash_password, verify_password
from backend.utils import now_ist

logger = logging.getLogger(__name__)


async def create_user(req: UserCreateRequest) -> UserResponse:
    """
    Creates a new user in MongoDB with a hashed password.
    """
    db = DatabaseManager.get_db()

    existing = await db.users.find_one({
        "$or": [
            {"pan_number": req.pan_number.upper()},
            {"email": req.email.lower()}
        ]
    })

    if existing:
        if existing["pan_number"] == req.pan_number.upper():
            raise ValueError("A user with this PAN already exists.")

        raise ValueError("A user with this email already exists.")

    user_id = generate_oid(
        req.first_name,
        req.middle_name,
        req.last_name,
        req.pan_number,
        req.aadhar_number,
        req.aadhar_pincode,
        req.mobile_number,
        req.email
    )

    user_doc = {
        "_id": user_id,
        "first_name": req.first_name,
        "middle_name": req.middle_name,
        "last_name": req.last_name,
        "pan_number": req.pan_number.upper(),
        "aadhar_number": req.aadhar_number,
        "aadhar_pincode": req.aadhar_pincode,
        "mobile_number": req.mobile_number,
        "email": req.email.lower(),
        "password": hash_password(req.password),
        "created_at": now_ist(),
        "updated_at": None
    }

    await db.users.insert_one(user_doc)
    return UserResponse(**user_doc)


async def login_user(req: UserLoginRequest) -> Optional[UserResponse]:
    """
    Verifies user credentials (PAN + Hashed Password).
    """
    db = DatabaseManager.get_db()

    user_doc = await db.users.find_one({"pan_number": req.pan_number.upper()})

    if user_doc and verify_password(req.password, user_doc["password"]):
        return UserResponse(**user_doc)

    return None


async def get_user_by_pan(pan_number: str) -> Optional[UserResponse]:
    db = DatabaseManager.get_db()

    user_doc = await db.users.find_one({"pan_number": pan_number.upper()})
    if user_doc:
        return UserResponse(**user_doc)

    return None


async def get_user_by_oid(oid: str) -> Optional[UserResponse]:
    db = DatabaseManager.get_db()

    try:
        user_doc = await db.users.find_one({"_id": ObjectId(oid)})
    except Exception:
        user_doc = await db.users.find_one({"_id": oid})

    if user_doc:
        return UserResponse(**user_doc)

    return None
