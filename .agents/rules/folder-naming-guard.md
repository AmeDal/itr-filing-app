---
description: Ensure the backend directory structure strictly follows the agreed-upon folder naming conventions.
---

# Folder Naming Guard

When creating or modifying backend files and folders in this project, you **MUST** strictly adhere to the following approved folder names, as defined in `AGENTS.md`.

## Allowed Folder Names
- `backend/controllers/` (for FastAPI routers)
- `backend/schemas/` (for Pydantic response/request models)
- `backend/services/` (for business logic)

## Strictly Prohibited Folder Names
- ❌ `backend/routers/` -> Use `backend/controllers/` instead.
- ❌ `backend/schema/` -> Use `backend/schemas/` instead.
- ❌ `backend/service/` -> Use `backend/services/` instead.

Do not drift from this pattern. Any violation of this rule will cause structural inconsistencies across the repository.
