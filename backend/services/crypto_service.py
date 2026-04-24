import asyncio
import base64
from typing import Any, Optional

from bson import Binary
from pymongo import MongoClient
from pymongo.encryption import Algorithm, ClientEncryption

from backend.logger import logger


class CryptoService:
    """
    Singleton managing CSFLE lifecycle: key vault, Data Encryption Key, encrypt/decrypt.

    Usage:
        await CryptoService.initialize(mongo_uri, master_key_b64, key_vault_ns)
        encrypted = await CryptoService.encrypt_field("argon2hash...")
        plaintext = await CryptoService.decrypt_field(encrypted)
        CryptoService.close()
    """

    _client_encryption: Optional[ClientEncryption] = None
    _sync_client: Optional[MongoClient] = None
    _data_key_id: Optional[Binary] = None

    _ALT_NAME = "itr-password-dek"
    _ALGORITHM_RANDOM = Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random
    _ALGORITHM_DETERMINISTIC = Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic

    @classmethod
    def initialize(cls, mongo_uri: str, master_key_b64: str,
                   key_vault_namespace: str) -> None:
        """
        Sets up the CSFLE infrastructure synchronously.

        Steps:
        1. Decode and validate the 96-byte local KMS master key.
        2. Create a sync MongoClient for the key vault collection.
        3. Build a `ClientEncryption` instance with the local KMS provider.
        4. Create or retrieve the Data Encryption Key (DEK) by altName.

        This is intentionally synchronous — it is called once from
        `DatabaseManager.initialize()` inside FastAPI's lifespan startup,
        which is already in an async context via `asyncio.to_thread`.
        """
        if cls._client_encryption is not None:
            logger.warning("CryptoService already initialized.")
            return

        # --- 1. Validate master key ---
        if not master_key_b64:
            raise ValueError(
                "CSFLE_MASTER_KEY is not set. "
                "Generate one with: python -c \"import os, base64; print(base64.b64encode(os.urandom(96)).decode())\""
            )

        try:
            master_key_bytes = base64.b64decode(master_key_b64)
        except Exception as exc:
            raise ValueError(
                f"CSFLE_MASTER_KEY is not valid base64: {exc}") from exc

        if len(master_key_bytes) != 96:
            raise ValueError(
                f"CSFLE_MASTER_KEY must decode to exactly 96 bytes, got {len(master_key_bytes)}."
            )

        # --- 2. Sync MongoDB client for key vault ---
        kms_providers = {"local": {"key": master_key_bytes}}
        cls._sync_client = MongoClient(mongo_uri)

        # --- 3. ClientEncryption instance ---
        cls._client_encryption = ClientEncryption(
            kms_providers=kms_providers,
            key_vault_namespace=key_vault_namespace,
            key_vault_client=cls._sync_client,
            codec_options=cls._sync_client.codec_options,
        )
        logger.info("CryptoService: ClientEncryption initialized.")

        # --- 4. Create or retrieve DEK ---
        cls._data_key_id = cls._get_or_create_dek()
        logger.info(f"CryptoService: DEK ready (altName='{cls._ALT_NAME}').")

    @classmethod
    def _get_or_create_dek(cls) -> Binary:
        """Finds an existing DEK by altName or creates a new one. Returns the DEK ID."""
        # Try to find existing DEK
        existing = cls._client_encryption.get_key_by_alt_name(cls._ALT_NAME)
        if existing:
            logger.debug(
                f"CryptoService: Reusing existing DEK '{cls._ALT_NAME}'.")
            return existing["_id"]

        # Create new DEK
        dek_id = cls._client_encryption.create_data_key(
            "local",
            key_alt_names=[cls._ALT_NAME],
        )
        logger.info(f"CryptoService: Created new DEK '{cls._ALT_NAME}'.")
        return dek_id

    @classmethod
    def _encrypt_sync(cls, value: Any, algorithm: str) -> Binary:
        """Synchronous encrypt — called via asyncio.to_thread."""
        if cls._client_encryption is None or cls._data_key_id is None:
            raise RuntimeError(
                "CryptoService not initialized. Call initialize() first.")

        # Guard for optional fields being None
        if value is None:
            return None

        return cls._client_encryption.encrypt(
            value,
            algorithm=algorithm,
            key_id=cls._data_key_id,
        )

    @classmethod
    def _decrypt_sync(cls, ciphertext: Binary) -> Any:
        """Synchronous decrypt — called via asyncio.to_thread."""
        if cls._client_encryption is None:
            raise RuntimeError(
                "CryptoService not initialized. Call initialize() first.")

        if ciphertext is None:
            return None

        return cls._client_encryption.decrypt(ciphertext)

    @classmethod
    async def encrypt_random(cls, value: Any) -> Binary:
        """
        Encrypts a highly sensitive field (e.g. password) that does NOT need to be queried.
        """
        return await asyncio.to_thread(cls._encrypt_sync, value,
                                       cls._ALGORITHM_RANDOM)

    @classmethod
    async def encrypt_deterministic(cls, value: Any) -> Binary:
        """
        Encrypts a sensitive field allowing for exact equality queries (Deterministic).
        Note: Booleans are automatically cast to int (1/0) because bool is not
        supported for deterministic encryption in many CSFLE implementations.
        """
        if isinstance(value, bool):
            value = 1 if value else 0
        return await asyncio.to_thread(cls._encrypt_sync, value,
                                       cls._ALGORITHM_DETERMINISTIC)

    @classmethod
    async def decrypt_field(cls, ciphertext: Binary) -> Any:
        """
        Decrypts a CSFLE-encrypted Binary field back to a string or original type.

        Runs in a thread to avoid blocking the async event loop.
        """
        return await asyncio.to_thread(cls._decrypt_sync, ciphertext)

    @classmethod
    def close(cls) -> None:
        """Releases the ClientEncryption and sync MongoClient resources."""
        if cls._client_encryption:
            cls._client_encryption.close()
            cls._client_encryption = None
            logger.info("CryptoService: ClientEncryption closed.")

        if cls._sync_client:
            cls._sync_client.close()
            cls._sync_client = None

        cls._data_key_id = None
