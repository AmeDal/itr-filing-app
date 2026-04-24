from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.controllers.admin_router import router as admin_router
from backend.controllers.itr_router import router as itr_router
from backend.controllers.user_router import router as user_router
from backend.controllers.filing_router import router as filing_router
from backend.db import DatabaseManager
from backend.services.blob_service import BlobStorageService
from backend.services.llm_service import close_client, get_client
from backend.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and connections
    await DatabaseManager.initialize()
    # Pre-initialize Gemini client
    get_client()
    yield
    # Shutdown: Close DB and cleanup
    await DatabaseManager.close()
    await BlobStorageService.close()
    await close_client()


app = FastAPI(
    title="ITR Filing App",
    description="Production-grade ITR Filing Application with native Async MongoDB and CSFLE",
    lifespan=lifespan
)
api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
api_router.include_router(user_router)
api_router.include_router(itr_router)
api_router.include_router(filing_router)
api_router.include_router(admin_router)
app.include_router(api_router)
