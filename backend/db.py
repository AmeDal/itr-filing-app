import logging
from contextlib import asynccontextmanager

import aiosqlite

from backend.settings import get_settings

from backend.logger import logger

# Schema Definitions
USERS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name  TEXT    NOT NULL,
    pan_number TEXT    NOT NULL UNIQUE 
                      CHECK(length(pan_number) = 10),
    aadhar_number TEXT UNIQUE 
                      CHECK(aadhar_number IS NULL OR length(aadhar_number) = 12),
    email      TEXT   UNIQUE,
    dob        TEXT,
    father_name TEXT,
    gender     TEXT   CHECK(gender IS NULL OR gender IN ('MALE','FEMALE','OTHER')),
    address_line TEXT,
    pincode    TEXT   CHECK(pincode IS NULL OR length(pincode) = 6),
    status     TEXT   NOT NULL DEFAULT 'active'
                      CHECK(status IN ('active','inactive','suspended')),
    created_at TEXT   NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT   NOT NULL DEFAULT (datetime('now'))
) STRICT;
"""

DOCUMENTS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS documents (
    id             TEXT    PRIMARY KEY,
    batch_id       TEXT    NOT NULL,
    user_id        INTEGER,
    doc_type       TEXT    NOT NULL
                          CHECK(doc_type IN ('PAN','AADHAR')),
    status         TEXT    NOT NULL DEFAULT 'queued'
                          CHECK(status IN ('queued','extracting','completed','error')),
    extracted_data TEXT,
    error_message  TEXT,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) STRICT;
"""

AUDIT_LOG_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS user_audit_log (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    field_name TEXT    NOT NULL,
    old_value  TEXT,
    new_value  TEXT,
    changed_at TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) STRICT;
"""

INDEXES_DDL = [
    "CREATE INDEX IF NOT EXISTS idx_users_pan ON users(pan_number);",
    "CREATE INDEX IF NOT EXISTS idx_documents_batch ON documents(batch_id);",
    "CREATE INDEX IF NOT EXISTS idx_audit_user ON user_audit_log(user_id);"
]

class DatabaseManager:
    _db_path = None

    @classmethod
    async def initialize(cls):
        """Startup initialization: creates tables and runs integrity checks."""
        settings = get_settings()
        cls._db_path = settings.db_path
        
        logger.info(f"Initializing database at {cls._db_path}")
        
        async with cls.get_db() as db:
            # Drop legacy tables if they exist (Renaming taxpayers -> users)
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='taxpayers'")
            if await cursor.fetchone():
                logger.warning("Legacy table 'taxpayers' found. Dropping it to migrate to 'users'.")
                await db.execute("DROP TABLE taxpayers")
            
            # Since we are overhauling even the valid documents table to STRICT and adding user_id
            await db.execute("DROP TABLE IF EXISTS documents")

            # Enable Foreign Keys & Write-Ahead Logging
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute("PRAGMA journal_mode = WAL")
            
            # Integrity Check
            cursor = await db.execute("PRAGMA integrity_check")
            result = await cursor.fetchone()
            if result[0] != "ok":
                logger.error(f"Database integrity check failed: {result[0]}")
                raise RuntimeError("Database integrity check failed")

            # Create Tables
            await db.execute(USERS_TABLE_DDL)
            await db.execute(DOCUMENTS_TABLE_DDL)
            await db.execute(AUDIT_LOG_TABLE_DDL)
            
            # Create Indexes
            for index_sql in INDEXES_DDL:
                await db.execute(index_sql)
            
            await db.commit()
            logger.info("Database initialization complete.")

    @classmethod
    @asynccontextmanager
    async def get_db(cls):
        """Async context manager for database connections."""
        if cls._db_path is None:
            cls._db_path = get_settings().db_path
            
        db = await aiosqlite.connect(cls._db_path)
        db.row_factory = aiosqlite.Row
        try:
            await db.execute("PRAGMA foreign_keys = ON")
            yield db
        finally:
            await db.close()

@asynccontextmanager
async def get_db_connection():
    async with DatabaseManager.get_db() as db:
        yield db
