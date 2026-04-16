---
description: Enforces layered architecture — routers handle routes only, services handle logic, DAL handles data access. No layer may contain another layer's responsibility.
alwaysApply: false
globs: ["backend/**/*.py"]
---

# Separation of Concerns Rule

## Layer Responsibilities

| Layer | File Pattern | Allowed | Forbidden |
|---|---|---|---|
| **Router** | `controllers/*_router.py` | Route definitions, HTTP status codes, call services | DB queries, business logic, data transforms |
| **Service** | `service/*_service.py` | Business logic, orchestrate DAL calls | Route definitions, direct DB queries, HTTP formatting |
| **DAL** | `dal/*_dal.py` or `db.py` | CRUD queries, connection management | Business logic, request validation |
| **Schema** | `schema/*_schema.py` | Pydantic request + response models | Business logic, DB queries |
| **Settings** | `settings.py` | Constants, API keys, paths (via `.env`) | Business logic, routes |

## Violations to Flag

| If you see... | It belongs in... |
|---|---|
| SQL/ORM query in a router | `dal/` or `db.py` |
| `if/else` business logic in a router | `service/` |
| `@router.get` in a service file | `controllers/` |
| Data transformation in DAL | `service/` |
| Hardcoded API key anywhere | `settings.py` via `.env` |
