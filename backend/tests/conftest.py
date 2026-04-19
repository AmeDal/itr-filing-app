import os
from pathlib import Path
from dotenv import load_dotenv

# Path to the test environment file
test_env_path = Path(__file__).parent.parent.parent / ".env.test"

# Force load the test environment variables, overriding ANY existing ones
if test_env_path.exists():
    load_dotenv(dotenv_path=test_env_path, override=True)
else:
    raise RuntimeError(f"FATAL: .env.test not found at {test_env_path}")

# Prevent settings from looking at the wrong file
os.environ["ENV_FILE"] = ".env.test"

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from pymongo import MongoClient

from backend.main import app
from backend.db import DatabaseManager
from backend.settings import get_settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def db_lifecycle(event_loop):
    """
    Initializes the database for the test session and guarantees cleanup.
    Pointed to the ephemeral 'itr_filing_integration_test' database.
    """
    # Force reload settings from the newly set ENV_FILE
    get_settings.cache_clear()
    settings = get_settings()

    # CRITICAL SECURITY CHECK: Ensure we are NOT wiping production
    if settings.mongo_db_name != "itr_filing_integration_test":
        raise RuntimeError(f"FATAL: Tests attempted to run against unexpected DB: {settings.mongo_db_name}")

    # Initialize connection
    await DatabaseManager.initialize()

    yield

    # CLEANUP PHASE: Destroy the ephemeral test database
    await DatabaseManager.close()

    # Use sync client for total destruction (bypassing Motor lifecycle issues during shutdown)
    sync_client = MongoClient(settings.mongo_uri)
    try:
        # Attempt to drop the entire database
        sync_client.drop_database(settings.mongo_db_name)
    except Exception:
        # Fallback: Individually drop collections if drop_database permission denied
        db = sync_client[settings.mongo_db_name]
        for collection in db.list_collection_names():
            db.drop_collection(collection)
    finally:
        sync_client.close()

@pytest.fixture(autouse=True)
async def db_cleanup():
    """
    Clears collections between individual tests to ensure test isolation.
    """
    db = DatabaseManager.get_db()
    # We don't drop the vault collections! Just the data.
    collections_to_clear = ["users", "filing_attempts"]
    for coll_name in collections_to_clear:
        if coll_name in await db.list_collection_names():
            await db[coll_name].delete_many({})

@pytest.fixture
async def async_client():
    """Returns an AsyncClient for testing the FastAPI application."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
