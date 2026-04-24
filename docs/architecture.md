# ITR Filing App — Architecture Overview

> **Living document** — update when architecture changes. Agents should reference specific sections, not the entire file.
> **Last updated**: 2026-04-24

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Document Processing Flow](#document-processing-flow)
- [Authentication & Authorization](#authentication--authorization)
- [Tech Stack](#tech-stack)
- [Key Design Decisions](#key-design-decisions)
- [Sub-Documents](#sub-documents)

---

## System Architecture

```mermaid
graph TB
    subgraph Frontend ["Frontend (React + Vite)"]
        AuthPage["AuthPage"]
        ITRSelect["ITRSelectionPage"]
        Upload["DocumentUploadPage"]
        Progress["ProgressDashboardPage"]
        Summary["SummaryPage"]
        FilingHistory["FilingHistoryPage"]
        AdminUsers["AdminUsersPage"]
        AuthCtx["AuthContext<br/>(token + theme state)"]
        API["api.js<br/>(fetchWithAuth + SSE)"]
    end

    subgraph Backend ["Backend (FastAPI + PyMongo Async)"]
        AuthDeps["auth_deps.py<br/>(get_current_user, require_admin)"]
        UserRouter["user_router.py<br/>(signup, login, refresh, logout, me)"]
        ITRRouter["itr_router.py<br/>(upload, progress SSE)"]
        FilingRouter["filing_router.py<br/>(history, delete document slot)"]
        AdminRouter["admin_router.py<br/>(user admin, reset, delete)"]
        SessionMgr["SessionManager<br/>(in-memory progress)"]
        Processing["ITRProcessingService<br/>(PDF pages -> Gemini -> JSON)"]
        FilingSvc["filing_service.py<br/>(filing_attempts persistence)"]
        Blocklist["token_blocklist.py<br/>(in-memory v1)"]
    end

    subgraph Storage ["Storage"]
        MongoDB[("MongoDB Atlas<br/>(users, filing_attempts, key vault)")]
        AzureBlob[("Azure Blob Storage<br/>(page extraction JSONs)")]
    end

    subgraph External ["External Services"]
        Gemini["Gemini API<br/>(document extraction)"]
    end

    Frontend -->|"Bearer JWT"| Backend
    API -->|"credentials: include"| UserRouter
    AuthDeps --> MongoDB
    UserRouter --> MongoDB
    ITRRouter --> SessionMgr
    ITRRouter --> FilingSvc
    SessionMgr --> Processing
    Processing --> Gemini
    Processing --> AzureBlob
    Processing --> FilingSvc
    FilingRouter --> FilingSvc
    FilingRouter --> AzureBlob
    AdminRouter --> MongoDB
    AdminRouter -->|"cascade delete"| AzureBlob
    FilingSvc --> MongoDB

    style Frontend fill:#4f46e5,color:#fff
    style Backend fill:#7c3aed,color:#fff
    style Storage fill:#0891b2,color:#fff
    style External fill:#d97706,color:#fff
```

---

## Document Processing Flow

```mermaid
flowchart TD
    A["AuthPage (Login)"] --> B["ITR Selection Page"]
    B --> C["Document Upload Page"]
    C --> D["Progress Dashboard"]
    D --> E["Filing History / Summary"]

    C -->|"Files + AY + ITR type + doc_types + Bearer"| F["POST /api/v1/itr/upload"]
    F -->|"user_id from JWT sub"| G["Upsert filing_attempts record"]
    G --> H{"Completed doc slot exists?"}
    H -->|"Yes"| I["400: delete completed slot before re-upload"]
    H -->|"No"| J["Create in-memory session"]

    J --> K["Background process_session"]
    K --> L["Get PDF page count off event loop"]
    L --> M{"Blob cache has existing pages?"}
    M -->|"All pages present"| N["Mark document completed"]
    M -->|"Missing pages"| O["Render missing pages at 200 DPI off event loop"]
    O --> P["Gemini API with retry"]
    P --> Q["Save page_{n}.json to Blob Storage"]
    Q --> R["Update filing_attempts document completion"]

    D <----|"SSE Stream via fetch-event-source"| S["GET /api/v1/itr/progress/{session_id}"]
    S --> J

    style A fill:#4f46e5,color:#fff
    style B fill:#4f46e5,color:#fff
    style C fill:#4f46e5,color:#fff
    style D fill:#4f46e5,color:#fff
    style G fill:#8b5cf6,color:#fff
    style K fill:#8b5cf6,color:#fff
```

---

## Authentication & Authorization

> Full details in [docs/auth.md](auth.md)

### Summary

- **JWT access + refresh** token pair with `PyJWT[crypto]`
- **Access token**: short-lived, configurable by `ACCESS_TOKEN_EXPIRE_MINUTES`, stored in React state, sent as `Authorization: Bearer`
- **Refresh token**: configurable by `REFRESH_TOKEN_EXPIRE_DAYS`, stored in an `HttpOnly` cookie scoped to `/api/v1/users/refresh`
- **Roles**: `admin` | `user` — stored encrypted in Mongo and carried in access token claims
- **Page refresh**: silent `/users/refresh` call restores session from cookie
- **Route guards**: `ProtectedRoute` checks auth/admin role in the UI; backend dependencies enforce access

### Auth Flow (condensed)

```mermaid
sequenceDiagram
    participant SPA
    participant API
    SPA->>API: POST /api/v1/users/login {username: PAN, password}
    API-->>SPA: {access_token, user} + Set-Cookie: refresh_token
    SPA->>API: GET /api/v1/itr/progress/{session_id} [Bearer]
    API-->>SPA: 200 SSE
    Note over SPA: Token expires...
    SPA->>API: POST /api/v1/users/refresh (cookie auto-sent)
    API-->>SPA: {access_token} + Set-Cookie: new_refresh_token
```

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 19 + Vite 8 | Fast HMR, simple app shell |
| **Routing** | react-router-dom 7 | Layout routes and protected route nesting |
| **Auth state** | React Context + in-memory access token | Keeps auth simple without localStorage access-token persistence |
| **SSE client** | `@microsoft/fetch-event-source` | Supports custom Bearer headers unlike native `EventSource` |
| **Backend** | FastAPI + Uvicorn | Async-native, auto-docs, Pydantic validation |
| **Database** | MongoDB Atlas + PyMongo | Native `AsyncMongoClient`, flexible document model |
| **Encryption** | CSFLE explicit encryption | PII encrypted at rest; synchronous crypto boundary offloaded via `asyncio.to_thread` |
| **Password hashing** | Argon2 via passlib | Memory-hard password hashing, offloaded to worker threads |
| **JWT** | PyJWT[crypto] | HS256 signing and validation |
| **Blob storage** | Azure Blob Storage async client | Per-user/AY/doc-type/hash hierarchy for extraction JSONs |
| **AI extraction** | Google Gemini API | Vision model for page-level document extraction |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Progressive agent loading** | Gemini starts with `GEMINI.md` + `AGENTS.md`; task-specific skills/docs/specs are opened only when relevant |
| **Development branch as default target** | Agent-created PRs target `development` even if GitHub remote HEAD points elsewhere |
| **In-memory source document handling** | Uploaded files are read into memory and processed without writing source PDFs to disk |
| **PyMuPDF offload** | PDF page counting and rasterization run via worker threads to keep the event loop responsive |
| **Concurrency** | `asyncio.Semaphore(5)` limits concurrent Gemini page calls |
| **Real-time progress** | `sse-starlette` + `fetch-event-source` broadcasts in-memory session state with Bearer auth |
| **MD5 page cache** | Blob Storage path-based caching skips already-extracted pages for the same user/AY/doc/hash |
| **Completed-slot protection** | Completed filing documents must be deleted from filing history before re-uploading a replacement |
| **HttpOnly refresh cookie** | Refresh tokens are not exposed to JavaScript and are path-scoped to the refresh endpoint |
| **Auth gate, not flow gate** | `ProtectedRoute` checks auth/admin role; page-specific prerequisites redirect at the page level |
| **Deterministic ObjectId** | User `_id` is a BSON ObjectId derived from a 12-byte BLAKE2b digest of normalized identity fields |
| **Sequential delete cascade** | Admin deletion removes filing attempts, blobs, then user profile; it is not a Mongo transaction |
| **In-memory token blocklist (v1)** | Zero-infra dev revocation with documented upgrade path to Mongo TTL in [auth.md](auth.md#6-token-blocklist-scaling) |

---

## Sub-Documents

Detailed architecture for specific subsystems. Reference these when working on related tasks.

| Document | Scope | When to reference |
|----------|-------|-------------------|
| [auth.md](auth.md) | JWT tokens, blocklist scaling, RBAC, route protection, admin operations | Any auth/authorization task, token handling, admin user management |
