# ITR Filing App — Codebase Map

> This file is the agent's primary navigation tool. Read it first, then open only the files relevant to the current task. Update it whenever files or folders are created, removed, or repurposed.

## Project Root

| Path | Responsibility |
|------|---------------|
| `.gemini/GEMINI.md` | Project-level AI rules and architecture guidelines |
| `.gemini/settings.json` | Antigravity context file configuration |
| `.gemini/skills/` | Gemini-visible OpenSpec workflow skills |
| `.gemini/commands/opsx/` | Gemini slash-command prompts for OpenSpec workflows |
| `.aiexclude` | Files excluded from AI context indexing |
| `.agents/rules/` | Always-on enforcement rules (async, separation of concerns, file size, PR branch) |
| `.agents/workflows/` | Slash-command workflows (`/new-endpoint`, `/new-page`, `/pre-push`) |
| `.agents/skills/` | Task-specific skills; open only the relevant skill for the current task |
| `AGENTS.md` | This file — codebase map |
| `openspec/specs/` | Active OpenSpec capability specs |
| `openspec/changes/archive/` | Archived OpenSpec changes; read only for historical rationale |
| `docs/` | Architecture documentation — see below |
| `.env` | All project secrets are stored here. Don't change the values here unless explicitly asked by user |
| `.env.example` | Non-secret environment variable template |
| `requirements.txt` | Backend/runtime/test Python dependencies |
| `package.json` | Root npm scripts for frontend dev/build/lint and backend startup |
| `vite.config.js` | Vite config with `frontend/` as root |
| `eslint.config.js` | Frontend ESLint config |
| `pytest.ini` | Pytest configuration |

## Branching

Treat `development` as the default integration branch for agent work and PR targets. Do not infer the working base from GitHub's remote default branch if it differs.

## Documentation (`docs/`)

> **Agent guidance:** Reference these docs **conditionally** — only read the specific doc relevant to your current task. Do not read the entire folder.

| Path | Scope | When to reference |
|------|-------|-------------------|
| `docs/architecture.md` | System overview, tech stack, design decisions | Understanding overall system or onboarding to codebase |
| `docs/auth.md` | JWT tokens, blocklist scaling, RBAC, threat model, admin ops | Any auth/authorization task, token handling, admin user management |

## Backend (`backend/`)

> **Status:** Async MongoDB via PyMongo `AsyncMongoClient`, in-memory ITR processing, Azure Blob persistence, CSFLE field encryption, JWT auth.

| Path | Responsibility |
|------|---------------|
| `backend/main.py` | FastAPI app init, router registration, lifespan, CORS |
| `backend/settings.py` | Pydantic BaseSettings singleton (constants, API keys, paths, credentials) |
| `backend/logger.py` | Unified logger → console + `logs/log.txt` |
| `backend/db.py` | MongoDB connection manager, indexes, seed admin user, deterministic ObjectId generation |
| `backend/security.py` | Password strength validation and Argon2 hash/verify helpers offloaded to worker threads |
| `backend/constants.py` | Shared `DocumentType` and `ITRType` enums |
| `backend/utils.py` | Shared helpers, compiled regex patterns |
| `backend/auth_deps.py` | OAuth2 scheme, `get_current_user`, `require_admin` dependencies |
| `backend/controllers/` | `*_router.py` — route definitions only |
| `backend/controllers/user_router.py` | Signup, login, refresh, logout, current-user routes |
| `backend/controllers/itr_router.py` | Multi-document upload and SSE progress stream |
| `backend/controllers/filing_router.py` | Filing history and document-slot deletion routes |
| `backend/controllers/admin_router.py` | Admin user list, role/status changes, reset password, cascade deletion |
| `backend/services/auth_service.py` | JWT issuance, validation, and token revocation helpers |
| `backend/services/blob_service.py` | Async Azure Blob Storage helpers for extraction JSONs and cleanup |
| `backend/services/crypto_service.py` | CSFLE key setup plus deterministic/random field encryption helpers |
| `backend/services/filing_service.py` | Filing attempt CRUD and document completion updates |
| `backend/services/itr_processing_service.py` | In-memory session manager and Gemini-backed page processing |
| `backend/services/llm_service.py` | Gemini client lifecycle, retry logic, and direct extraction helpers |
| `backend/services/pdf_service.py` | Shared PDF helpers that offload PyMuPDF parsing/rasterization to worker threads |
| `backend/services/prompt_templates.py` | Doc-type specific Gemini prompts |
| `backend/services/token_blocklist.py` | JWT revocation blocklist (in-memory v1) |
| `backend/services/user_deletion_service.py` | Cascade hard-delete (Mongo + Azure Blobs) |
| `backend/services/user_service.py` | User creation, login lookup, decryption, and read helpers |
| `backend/services/` | `*_service.py` — business logic, one file per task |
| `backend/schemas/user_schema.py` | User, auth, and token response schemas |
| `backend/schemas/filing_schema.py` | Filing attempt and document schemas |
| `backend/schemas/extraction_schema.py` | PAN/Aadhar direct extraction schemas retained for service helpers/tests |
| `backend/schemas/` | `*_schema.py` — Pydantic request + response schemas |
| `backend/tests/` | Backend unit and integration tests |

> Create `backend/dal/` only if `db.py` grows beyond connection/index/seed responsibilities.

## Frontend (`frontend/`)

> **Status:** Authenticated ITR journey, filing history, admin user management, theme toggle, JWT auth.

| Path | Responsibility |
|------|---------------|
| `frontend/src/App.jsx` | Root component, routing (react-router-dom), AuthProvider wrapper |
| `frontend/src/pages/AuthPage.jsx` | Login/signup page |
| `frontend/src/pages/ITRSelectionPage.jsx` | Assessment year and ITR type selection |
| `frontend/src/pages/DocumentUploadPage.jsx` | Required/optional document upload flow |
| `frontend/src/pages/ProgressDashboardPage.jsx` | SSE-backed processing progress UI |
| `frontend/src/pages/SummaryPage.jsx` | Post-processing summary placeholder |
| `frontend/src/pages/FilingHistoryPage.jsx` | User filing history and document deletion |
| `frontend/src/pages/AdminUsersPage.jsx` | Admin user management page |
| `frontend/src/pages/` | Route-level page components |
| `frontend/src/components/upload/` | FileDropzone and upload-related components |
| `frontend/src/components/shared/` | Reusable UI elements (ProtectedRoute, UserMenu, AppLayout, ThemeToggle) |
| `frontend/src/context/` | React Context providers (AuthContext) |
| `frontend/src/services/api.js` | API service with SSE support, Bearer auth, refresh interceptor |
| `frontend/src/constants/docTypes.js` | Frontend document and ITR type constants |
| `frontend/src/index.css` | Global app styles and theme tokens |
| `frontend/src/assets/` | Frontend image/SVG assets |
