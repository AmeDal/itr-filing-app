---
name: fastapi-backend
description: Activate this skill when the user is working on backend Python code, FastAPI endpoints, database operations, Pydantic schemas, or any server-side logic. This skill provides architecture patterns, async best practices, and project-specific conventions for the FastAPI backend.
---

# FastAPI Backend Skill

## Architecture Reference

```
backend/
├── controllers/     # Route definitions only
├── dal/             # Data Access Layer (when db.py grows)
├── models/          # DB models (when >5 tables)
├── schemas/         # Pydantic request + response schemas
├── services/        # Business logic (one file per task)
├── utils.py         # Shared helpers
├── db.py            # DB connection + CRUD (while small)
├── logger.py        # Unified logger
├── settings.py      # Pydantic BaseSettings singleton
└── main.py          # FastAPI app init
```

## Patterns to Follow

### FastAPI App Initialization (`main.py`)
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB connections, caches, etc.
    await startup()
    yield
    # Shutdown: close connections
    await shutdown()

app = FastAPI(title="ITR Filing App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Pydantic BaseSettings (`settings.py`)
```python
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Logger Setup (`logger.py`)
```python
import logging
from pathlib import Path


def setup_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "log.txt")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
```

### Service Pattern
```python
# services/user_service.py
from db import get_user_by_id, insert_user
from schemas.user_schema import CreateUserRequest


async def create_user(req: CreateUserRequest) -> dict:
    # Business logic here — validation, transformation, orchestration
    user = await insert_user(req.name, req.email)
    return user


async def get_user(user_id: int) -> dict:
    user = await get_user_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user
```

### Router Pattern
```python
# controllers/user_router.py
from fastapi import APIRouter, HTTPException
from schemas.user_schema import CreateUserRequest, UserResponse
from services.user_service import create_user, get_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user_endpoint(req: CreateUserRequest):
    return await create_user(req)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int):
    try:
        return await get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## db.py → DAL Migration Checklist

When `db.py` exceeds ~300 lines or has CRUD for multiple domains:

1. Create `dal/` directory
2. Create `dal/*_dal.py` — one file per domain
3. Move domain-specific CRUD functions from `db.py` to the appropriate DAL file
4. Keep connection management and table definitions in `db.py`
5. Update imports across all service files
6. Update `AGENTS.md`

## Dependency Injection

Use FastAPI's `Depends()` for shared resources:

```python
from fastapi import Depends
from settings import Settings, get_settings


@router.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```
