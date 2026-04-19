from typing import Optional

from bson import ObjectId

from backend.db import DatabaseManager, generate_oid
from backend.schemas.user_schema import UserCreateRequest, UserLoginRequest, UserResponse
from backend.security import hash_password, verify_password
from backend.services.crypto_service import CryptoService
from backend.utils import now_ist


async def decrypt_user_doc(
        user_doc: Optional[dict],
        skip_fields: Optional[set] = None) -> Optional[dict]:
    """
    Helper to decrypt all encrypted fields in a user document before returning.
    Skips fields in skip_fields set. Password is skipped by default if skip_fields is not provided.
    """
    if not user_doc:
        return None

    doc = user_doc.copy()
    if skip_fields is None:
        skip_fields = {"password"}

    fields_to_decrypt = [
        "first_name", "middle_name", "last_name", "pan_number",
        "aadhar_number", "aadhar_pincode", "mobile_number", "email",
        "password", "role", "is_active"
    ]
    for field in fields_to_decrypt:
        if field in doc and doc[field] is not None and field not in skip_fields:
            doc[field] = await CryptoService.decrypt_field(doc[field])

    return doc


async def create_user(req: UserCreateRequest) -> UserResponse:
    """
    Creates a new user in MongoDB with a hashed password.
    """
    db = DatabaseManager.get_db()

    enc_pan = await CryptoService.encrypt_deterministic(req.pan_number.upper())
    enc_email = await CryptoService.encrypt_deterministic(req.email.lower())

    existing = await db.users.find_one(
        {"$or": [{
            "pan_number": enc_pan
        }, {
            "email": enc_email
        }]})

    if existing:
        # Check against the search encrypted values
        if existing["pan_number"] == enc_pan:
            raise ValueError("A user with this PAN already exists.")

        raise ValueError("A user with this email already exists.")

    user_id = generate_oid(req.first_name, req.middle_name, req.last_name,
                           req.pan_number, req.aadhar_number,
                           req.aadhar_pincode, req.mobile_number, req.email)

    user_doc = {
        "_id":
        user_id,
        "first_name":
        await CryptoService.encrypt_deterministic(req.first_name),
        "middle_name":
        await CryptoService.encrypt_deterministic(req.middle_name)
        if req.middle_name else None,
        "last_name":
        await CryptoService.encrypt_deterministic(req.last_name),
        "pan_number":
        enc_pan,
        "aadhar_number":
        await CryptoService.encrypt_deterministic(req.aadhar_number),
        "aadhar_pincode":
        await CryptoService.encrypt_deterministic(req.aadhar_pincode),
        "mobile_number":
        await CryptoService.encrypt_deterministic(req.mobile_number),
        "email":
        enc_email,
        "password":
        await CryptoService.encrypt_random(hash_password(req.password)),
        "role":
        await CryptoService.encrypt_deterministic(getattr(req, "role",
                                                          "user")),
        "is_active":
        await CryptoService.encrypt_deterministic(True),
        "created_at":
        now_ist(),
        "updated_at":
        None
    }

    await db.users.insert_one(user_doc)
    decrypted_doc = await decrypt_user_doc(user_doc)
    return UserResponse(**decrypted_doc)


async def login_user(req: UserLoginRequest) -> Optional[UserResponse]:
    """
    Verifies user credentials (PAN + Hashed Password).
    """
    db = DatabaseManager.get_db()

    enc_pan = await CryptoService.encrypt_deterministic(req.pan_number.upper())
    user_doc = await db.users.find_one({"pan_number": enc_pan})

    if user_doc and "password" in user_doc:
        decrypted_hash = await CryptoService.decrypt_field(user_doc["password"]
                                                           )
        if verify_password(req.password, decrypted_hash):
            decrypted_doc = await decrypt_user_doc(user_doc)
            return UserResponse(**decrypted_doc)

    return None


async def get_user_by_pan(pan_number: str) -> Optional[UserResponse]:
    db = DatabaseManager.get_db()

    enc_pan = await CryptoService.encrypt_deterministic(pan_number.upper())
    user_doc = await db.users.find_one({"pan_number": enc_pan})
    if user_doc:
        decrypted_doc = await decrypt_user_doc(user_doc)
        return UserResponse(**decrypted_doc)

    return None


async def get_user_by_oid(oid: str) -> Optional[UserResponse]:
    db = DatabaseManager.get_db()

    try:
        user_doc = await db.users.find_one({"_id": ObjectId(oid)})
    except Exception:
        user_doc = await db.users.find_one({"_id": oid})

    if user_doc:
        decrypted_doc = await decrypt_user_doc(user_doc)
        return UserResponse(**decrypted_doc)

    return None
