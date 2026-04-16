---
description: Step-by-step guide to add a new FastAPI endpoint following the project architecture.
---

# Add New Endpoint

Follow these steps **in order** when adding a new API endpoint.

---

## Step 1: Define Schema

Open or create `backend/schema/*_schema.py` for the relevant domain.

1. Create a **request** Pydantic model (if the endpoint accepts a body)
2. Create a **response** Pydantic model
3. Keep both in the same file, grouped by domain

```python
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

---

## Step 2: Create Service

Open or create `backend/service/*_service.py` for the logical task.

1. Implement the business logic as an `async def` function
2. Call `db.py` or `dal/` for data access — never write SQL here
3. Return the result (not an HTTP response)

```python
async def create_user(name: str, email: str) -> dict:
    user = await db.insert_user(name, email)
    return user
```

---

## Step 3: Create Router

Open or create `backend/controllers/*_router.py`.

1. Define the route using `@router.post(...)` or `@router.get(...)`
2. Call the service function — no business logic here
3. Return the response using the schema model

```python
from fastapi import APIRouter
from schema.user_schema import CreateUserRequest, UserResponse
from service.user_service import create_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user_endpoint(req: CreateUserRequest):
    return await create_user(req.name, req.email)
```

---

## Step 4: Register Router

In `backend/main.py`, add:

```python
from controllers.user_router import router as user_router
app.include_router(user_router)
```

---

## Step 5: Update AGENTS.md

Add entries for any new files created in this workflow.

---

## Checklist

- [ ] Schema defined (request + response in same file)
- [ ] Service created (async, business logic only)
- [ ] Router created (route definition only, calls service)
- [ ] Router registered in `main.py`
- [ ] `AGENTS.md` updated
