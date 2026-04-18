from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db import DatabaseManager
from backend.controllers import extraction_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await DatabaseManager.initialize()
    yield
    # Shutdown
    pass


app = FastAPI(title="ITR Filing App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extraction_router, prefix="/api")
app.include_router(user_router, prefix="/api")


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

