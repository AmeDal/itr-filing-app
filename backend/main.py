from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.controllers.extraction_router import router as extraction_router
from backend.controllers.user_router import router as user_router
from backend.db import DatabaseManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and connections
    await DatabaseManager.initialize()
    yield
    # Shutdown: Close DB and cleanup
    await DatabaseManager.close()


app = FastAPI(
    title="ITR Filing App",
    description="Production-grade ITR Filing Application with Async MongoDB",
    lifespan=lifespan
)

# Shared API Router for versioning and prefixes
api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
api_router.include_router(extraction_router)
api_router.include_router(user_router)
app.include_router(api_router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
