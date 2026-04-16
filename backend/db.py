from contextlib import asynccontextmanager

import aiosqlite

DB_FILE = "app.db"


async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS taxpayers (
                pan_number TEXT PRIMARY KEY,
                aadhar_number TEXT,
                first_name TEXT,
                middle_name TEXT,
                last_name TEXT,
                dob DATE,
                father_name TEXT,
                gender TEXT,
                address_line TEXT,
                pincode TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                batch_id TEXT,
                pan_number TEXT,
                doc_type TEXT,
                file_path TEXT,
                extracted_data TEXT,
                status TEXT,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pan_number) REFERENCES taxpayers (pan_number)
            )
        ''')

        # Add columns if they don't exist (primitive migration)
        cursor = await db.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in await cursor.fetchall()]
        if "batch_id" not in columns:
            await db.execute("ALTER TABLE documents ADD COLUMN batch_id TEXT")
        if "error_message" not in columns:
            await db.execute("ALTER TABLE documents ADD COLUMN error_message TEXT")

        await db.commit()


@asynccontextmanager
async def get_db_connection():
    db = await aiosqlite.connect(DB_FILE)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

