# ITR Filing App — Codebase Map

> This file is the agent's primary navigation tool. Update it whenever new files or folders are created.

## Project Root

| Path | Responsibility |
|------|---------------|
| `.gemini/GEMINI.md` | Project-level AI rules and architecture guidelines |
| `.gemini/settings.json` | Antigravity context file configuration |
| `.aiexclude` | Files excluded from AI context indexing |
| `.agents/rules/` | Always-on enforcement rules (async, separation of concerns, file size) |
| `.agents/workflows/` | Slash-command workflows (`/new-endpoint`, `/new-page`, `/pre-push`) |
| `.agents/skills/` | Auto-activated skills (fastapi-backend, react-frontend) |
| `AGENTS.md` | This file — codebase map |

## Backend (`backend/`)

> **Status:** Created and aligned.

| Path | Responsibility |
|------|---------------|
| `backend/main.py` | FastAPI app init, router registration, lifespan (DB init), CORS |
| `backend/settings.py` | Pydantic BaseSettings singleton (including DB path) |
| `backend/logger.py` | Unified logger → console + `logs/log.txt` |
| `backend/db.py` | DatabaseManager: STRICT schemas, WAL mode, integrity checks |
| `backend/utils.py` | Shared helpers, compiled regex patterns |
| `backend/controllers/` | `user_router.py`, `extraction_router.py` |
| `backend/services/` | `user_service.py` (business logic, UPSERTs), `batch_service.py` |
| `backend/schemas/` | `user_schema.py`, `extraction_schema.py` |

## Frontend (`frontend/`)

> **Status:** Not yet created. Will follow the structure defined in `.gemini/GEMINI.md`.

| Path | Responsibility |
|------|---------------|
| `frontend/src/App.jsx` | Root component, routing |
| `frontend/src/pages/` | One component per page |
| `frontend/src/components/shared/` | Reusable UI elements |
| `frontend/src/components/<page>/` | Page-specific sub-components |
| `frontend/src/services/` | Centralized API service functions |
| `frontend/src/hooks/` | Custom React hooks |
| `frontend/src/styles/` | CSS files |
