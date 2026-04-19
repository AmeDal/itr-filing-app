import hashlib
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from backend.logger import logger
from backend.security import hash_password
from backend.services.crypto_service import CryptoService
from backend.settings import get_settings
from backend.utils import mask_uri, now_ist


def generate_oid(first_name: str, middle_name: str, last_name: str,
                 pan_number: str, aadhar_number: str, aadhar_pincode: str,
                 mobile_number: str, email: str) -> ObjectId:
    """
    Generates a deterministic BSON ObjectId from core identity fields.

    The input fields are normalized (trimmed and case-adjusted where appropriate)
    and concatenated into a single string. A 12-byte BLAKE2b hash is then computed
    and used directly as the binary value for the ObjectId.

    Note:
    The resulting ObjectId is deterministic: identical input data will always
    produce the same ObjectId.
    """
    data = "|".join([
        first_name.strip().lower(),
        middle_name.strip().lower(),
        last_name.strip().lower(),
        pan_number.strip().upper(),
        aadhar_number.strip(),
        aadhar_pincode.strip(),
        mobile_number.strip(),
        email.strip().lower()
    ])
    full_hash = hashlib.blake2b(data.encode('utf-8'), digest_size=12).digest()
    return ObjectId(full_hash)


class DatabaseManager:
    """
    Singleton manager for MongoDB connection using Motor.
    Obsessively async and lifespan-safe.
    """
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def initialize(cls):
        """
        Connects to MongoDB and performs startup tasks like indexing and seeding.
        Should be called in the FastAPI lifespan startup.
        """
        if cls.client is not None:
            logger.warning("DatabaseManager already initialized.")
            return

        settings = get_settings()
        masked_uri = mask_uri(settings.mongo_uri)
        logger.info(f"Connecting to MongoDB at {masked_uri}")

        try:
            cls.client = AsyncIOMotorClient(settings.mongo_uri)
            cls.db = cls.client[settings.mongo_db_name]

            # Verify connection with a ping
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

            # Initialize CryptoService for CSFLE
            CryptoService.initialize(
                mongo_uri=settings.mongo_uri,
                master_key_b64=settings.csfle_master_key,
                key_vault_namespace=settings.csfle_key_vault_namespace
            )

            # Perform indexing and seeding
            await cls._ensure_indexes()
            await cls._seed_admin_user()

            logger.info("Database initialization complete.")
        except Exception as e:
            logger.error(f"Critical error during database initialization: {e}")
            raise e

    @classmethod
    async def _ensure_indexes(cls):
        """Ensures required indexes exist."""
        await cls.db.users.create_index("pan_number", unique=True)
        await cls.db.users.create_index("email", unique=True, sparse=True)
        await cls.db.filing_attempts.create_index([("user_id", 1), ("assessment_year", 1)], unique=True)

    @classmethod
    async def _seed_admin_user(cls):
        """Seeds the initial administrative user if not exists."""
        settings = get_settings()
        seed_data = settings.get_seed_user_dict()

        identity_fields = {
            k: v
            for k, v in seed_data.items() if k not in ("password", "role", "is_active")
        }
        user_id = generate_oid(**identity_fields)

        existing = await cls.db.users.find_one({"_id": user_id})
        if not existing:
            logger.info(f"Seeding initial user with _id: {user_id}")
            seed_data = seed_data.copy()

            # Encrypt identity fields deterministically
            identity_fields_to_encrypt = [
                "first_name", "middle_name", "last_name", "pan_number",
                "aadhar_number", "aadhar_pincode", "mobile_number", "email"
            ]
            for field in identity_fields_to_encrypt:
                if field in seed_data and seed_data[field]:
                    seed_data[field] = await CryptoService.encrypt_deterministic(seed_data[field])

            plain_pwd = seed_data["password"]
            hashed_pwd = hash_password(plain_pwd)
            seed_data["password"] = await CryptoService.encrypt_random(hashed_pwd)

            user_doc = {
                "_id": user_id,
                **seed_data,
                "role": await CryptoService.encrypt_deterministic(seed_data.get("role", "admin")),
                "is_active": await CryptoService.encrypt_deterministic(seed_data.get("is_active", True)),
                "created_at": now_ist(),
                "updated_at": None
            }
            await cls.db.users.insert_one(user_doc)
        else:
            # Migration: ensure existing seed user has role and is_active
            if "role" not in existing or "is_active" not in existing:
                logger.info(f"Updating seed user {user_id} with role/is_active")
                await cls.db.users.update_one(
                    {"_id": user_id},
                    {"$set": {
                        "role": await CryptoService.encrypt_deterministic(seed_data.get("role", "admin")),
                        "is_active": await CryptoService.encrypt_deterministic(seed_data.get("is_active", True))
                    }}
                )
            logger.debug("Seed user already exists.")

    @classmethod
    def get_db(cls):
        """Returns the database instance. Raises RuntimeError if not initialized."""
        if cls.db is None:
            raise RuntimeError(
                "DatabaseManager not initialized. Call initialize() first.")
        return cls.db

    @classmethod
    async def close(cls):
        """Closes the MongoDB connection."""
        CryptoService.close()
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed.")


async def get_db():
    """FastAPI dependency for obtaining the database instance."""
    return DatabaseManager.get_db()
