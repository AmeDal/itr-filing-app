import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from dotenv import load_dotenv

# Force loading test variables BEFORE anything else initializes
load_dotenv(".env.test", override=True)

from backend.main import app
from backend.db import DatabaseManager
from backend.settings import get_settings

@pytest.fixture(scope="session", autouse=True)
async def db_init():
    """
    Initializes the database using settings overridden by .env.test.
    Runs once per test session.
    """
    settings = get_settings()
    
    # CRITICAL SECURITY CHECK
    if not settings.mongo_db_name.endswith("_test"):
        raise RuntimeError(f"FATAL: Tests attempted to run against non-test DB: {settings.mongo_db_name}")
        
    await DatabaseManager.initialize()
    yield
    await DatabaseManager.close()

@pytest.fixture(scope="function")
async def db_cleanup():
    """
    Wipes the collections completely before each test guaranteeing isolation.
    """
    db = DatabaseManager.get_db()
    await db.users.delete_many({})
    await db.documents.delete_many({})
    
    # We must explicitly re-trigger seeding if needed by the app logic
    await DatabaseManager._seed_admin_user()
    
    yield

@pytest.fixture(scope="function")
async def async_client(db_cleanup):
    """
    HTTPX AsyncClient bound to the FastAPI application.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
