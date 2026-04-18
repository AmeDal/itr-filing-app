# ITR Filing App — Codebase Map

> This file is the agent's primary navigation tool. Update it whenever new files or folders are created but dont remove existing info unless that has been changed too.

## Project Root

| Path | Responsibility |
|------|---------------|
| `.gemini/GEMINI.md` | Project-level AI rules and architecture guidelines |
| `.gemini/settings.json` | Antigravity context file configuration |
| `.aiexclude` | Files excluded from AI context indexing |
| `.agents/rules/` | Always-on enforcement rules (async, separation of concerns, file size, PR branch) |
| `.agents/workflows/` | Slash-command workflows (`/new-endpoint`, `/new-page`, `/pre-push`) |
| `.agents/skills/` | Auto-activated skills (fastapi-backend, react-frontend) |
| `AGENTS.md` | This file — codebase map |
| `openspec/` | OpenSpec change artifacts (proposals, designs, specs, tasks) |
| `docs/` | Project documentation (e.g., architecture) |
| `.env` | All project secrets are stored here. Don't change the values here unless explicitly asked by user |

## Backend (`backend/`)

> **Status:** Migrated to Async MongoDB (`motor`). Extended with In-Memory ITR Processing & Azure Blob.

| Path | Responsibility |
|------|---------------|
| `backend/main.py` | FastAPI app init, router registration, lifespan, CORS |
| `backend/settings.py` | Pydantic BaseSettings singleton (constants, API keys, paths, credentials) |
| `backend/logger.py` | Unified logger → console + `logs/log.txt` |
| `backend/db.py` | DB connection, table definitions, CRUD (while small) |
| `backend/utils.py` | Shared helpers, compiled regex patterns |
| `backend/controllers/` | `*_router.py` — route definitions only |
| `backend/services/prompt_templates.py` | Doc-type specific Gemini prompts |
| `backend/services/` | `*_service.py` — business logic, one file per task |
| `backend/schemas/` | `*_schema.py` — Pydantic request + response schemas |
| `backend/dal/` | `*_dal.py` — created only when `db.py` grows too large |
| `backend/models/` | `*_model.py` — created only when >5 tables |

## Frontend (`frontend/`)

> **Status:** Redesigned with Dark Premium Auth UI & Full ITR Journey.

| Path | Responsibility |
|------|---------------|
| `frontend/src/App.jsx` | Root component, routing (react-router-dom) |
| `frontend/src/pages/` | Auth, ITR Selection, Upload, Progress, Summary pages |
| `frontend/src/components/upload/` | FileDropzone and upload-related components |
| `frontend/src/components/shared/` | Reusable UI elements |
| `frontend/src/components/<page>/` | Page-specific sub-components |
| `frontend/src/services/api.js` | API service with SSE support |
| `frontend/src/hooks/` | Custom React hooks |
| `frontend/src/styles/` | CSS files |