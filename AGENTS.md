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
| `docs/` | Architecture documentation — see below |
| `.env` | All project secrets are stored here. Don't change the values here unless explicitly asked by user |

## Documentation (`docs/`)

> **Agent guidance:** Reference these docs **conditionally** — only read the specific doc relevant to your current task. Do not read the entire folder.

| Path | Scope | When to reference |
|------|-------|-------------------|
| `docs/architecture.md` | System overview, tech stack, design decisions | Understanding overall system or onboarding to codebase |
| `docs/auth.md` | JWT tokens, blocklist scaling, RBAC, threat model, admin ops | Any auth/authorization task, token handling, admin user management |

## Backend (`backend/`)

> **Status:** Async MongoDB (`motor`), In-Memory ITR Processing, Azure Blob, JWT Auth (implemented).

| Path | Responsibility |
|------|---------------|
| `backend/main.py` | FastAPI app init, router registration, lifespan, CORS |
| `backend/settings.py` | Pydantic BaseSettings singleton (constants, API keys, paths, credentials) |
| `backend/logger.py` | Unified logger → console + `logs/log.txt` |
| `backend/db.py` | DB connection, table definitions, CRUD (while small) |
| `backend/utils.py` | Shared helpers, compiled regex patterns |
| `backend/auth_deps.py` | OAuth2 scheme, `get_current_user`, `require_admin` dependencies |
| `backend/controllers/` | `*_router.py` — route definitions only |
| `backend/services/prompt_templates.py` | Doc-type specific Gemini prompts |
| `backend/services/token_blocklist.py` | JWT revocation blocklist (in-memory v1) |
| `backend/services/auth_service.py` | JWT issuance and validation logic |
| `backend/services/user_deletion_service.py` | Cascade hard-delete (Mongo + Azure Blobs) |
| `backend/services/` | `*_service.py` — business logic, one file per task |
| `backend/schemas/` | `*_schema.py` — Pydantic request + response schemas |
| `backend/dal/` | `*_dal.py` — created only when `db.py` grows too large |
| `backend/models/` | `*_model.py` — created only when >5 tables |

## Frontend (`frontend/`)

> **Status:** Dark Premium Auth UI, Full ITR Journey, JWT Auth (implemented).

| Path | Responsibility |
|------|---------------|
| `frontend/src/App.jsx` | Root component, routing (react-router-dom), AuthProvider wrapper |
| `frontend/src/pages/` | Auth, ITR Selection, Upload, Progress, Summary, AdminUsers pages |
| `frontend/src/components/upload/` | FileDropzone and upload-related components |
| `frontend/src/components/shared/` | Reusable UI elements (ProtectedRoute, UserMenu, AppLayout, ThemeToggle) |
| `frontend/src/components/<page>/` | Page-specific sub-components |
| `frontend/src/context/` | React Context providers (AuthContext) |
| `frontend/src/services/api.js` | API service with SSE support, Bearer auth, refresh interceptor |
| `frontend/src/hooks/` | Custom React hooks |
| `frontend/src/styles/` | CSS files |