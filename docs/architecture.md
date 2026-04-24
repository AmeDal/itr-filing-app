# ITR Filing App — Architecture Overview

> **Living document** — update when architecture changes. Agents should reference specific sections, not the entire file.
> **Last updated**: 2026-04-19

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
        AdminUsers["AdminUsersPage"]
        AuthCtx["AuthContext<br/>(token state)"]
        API["api.js<br/>(fetchWithAuth + SSE)"]
    end

    subgraph Backend ["Backend (FastAPI + Motor)"]
        AuthDeps["auth_deps.py<br/>(get_current_user, require_admin)"]
        UserRouter["user_router.py<br/>(login, signup, refresh, logout)"]
        ITRRouter["itr_router.py<br/>(upload, progress SSE)"]
        ExtractRouter["extraction_router.py<br/>(batch, single)"]
        AdminRouter["admin_router.py<br/>(CRUD, delete cascade)"]
        SessionMgr["SessionManager<br/>(in-memory progress)"]
        Processing["ITRProcessingService<br/>(PDF→Gemini→JSON)"]
        Blocklist["token_blocklist<br/>(in-memory v1)"]
    end

    subgraph Storage ["Storage"]
        MongoDB[("MongoDB Atlas<br/>(users, documents, batches)")]
        AzureBlob[("Azure Blob Storage<br/>(extraction JSONs)")]
    end

    subgraph External ["External Services"]
        Gemini["Gemini API<br/>(document extraction)"]
    end

    Frontend -->|"Bearer JWT"| Backend
    API -->|"credentials: include"| UserRouter
    AuthDeps --> MongoDB
    ITRRouter --> SessionMgr
    SessionMgr --> Processing
    Processing --> Gemini
    Processing --> AzureBlob
    ExtractRouter --> MongoDB
    AdminRouter --> MongoDB
    AdminRouter -->|"cascade delete"| AzureBlob

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

    C -->|"Files + metadata + Bearer"| E["POST /api/v1/itr/upload"]
    E -->|"user_id from JWT sub"| F["Processing Engine"]

    F --> G{"MD5 Check Blob Storage"}
    G -->|"Exists & Complete"| H["Skip → Mark Completed"]
    G -->|"Missing/Incomplete"| I["Queue for Processing"]

    I --> J["Async Semaphore Pool (batch=5)"]
    J --> K["PDF → 200 DPI Images (in-memory)"]
    K --> L["Gemini API + Dynamic Prompt"]
    L --> M["Save JSON to Blob Storage"]

    D <----|"SSE Stream (Bearer via fetch-event-source)"| N["GET /api/v1/itr/progress/{session_id}"]
    N --> F

    style A fill:#4f46e5,color:#fff
    style B fill:#4f46e5,color:#fff
    style C fill:#4f46e5,color:#fff
    style D fill:#4f46e5,color:#fff
    style F fill:#8b5cf6,color:#fff
    style J fill:#8b5cf6,color:#fff
```

---

## Authentication & Authorization

> Full details in [docs/auth.md](auth.md)

### Summary

- **JWT access + refresh** token pair with `PyJWT[crypto]`
- **Access token**: short-lived (30 min), in-memory (React state), sent as `Authorization: Bearer`
- **Refresh token**: long-lived (7 days), `HttpOnly; Secure; SameSite=Strict` cookie
- **Roles**: `admin` | `user` — stored in `users.role`, carried in access token claims
- **Page refresh**: silent `/users/refresh` call restores session from cookie
- **Route guards**: `ProtectedRoute` checks auth only (not page flow); backend enforces ownership

### Auth Flow (condensed)

```mermaid
sequenceDiagram
    participant SPA
    participant API
    SPA->>API: POST /users/login {pan, password}
    API-->>SPA: {access_token, user} + Set-Cookie: refresh_token
    SPA->>API: GET /itr/upload [Bearer]
    API-->>SPA: 200 OK
    Note over SPA: Token expires...
    SPA->>API: POST /users/refresh (cookie auto-sent)
    API-->>SPA: {access_token} + Set-Cookie: new_refresh
```

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + Vite | Fast HMR, minimal config |
| **Routing** | react-router-dom v6 | Nested routes, layout routes |
| **Auth state** | React Context + in-memory tokens | No external state library needed for auth |
| **SSE client** | `@microsoft/fetch-event-source` | Supports custom headers (Bearer) unlike native `EventSource` |
| **Backend** | FastAPI + Uvicorn | Async-native, auto-docs, Pydantic validation |
| **Database** | MongoDB Atlas + Motor | Async driver, flexible schema for document extraction |
| **Encryption** | CSFLE (Client-Side Field Level) | PII encrypted at rest; deterministic for indexed lookups |
| **Password hashing** | Argon2 (via passlib) | Winner of PHC 2015; 64MB memory cost |
| **JWT** | PyJWT[crypto] | Actively maintained; HS256 signing |
| **Blob storage** | Azure Blob Storage (async) | Per-user/AY/doc-type hierarchy; MD5 dedup caching |
| **AI extraction** | Google Gemini API | Vision model for document-to-JSON extraction |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **In-memory buffer** | `io.BytesIO` and `fitz` stream for zero-disk persistence of uploaded files |
| **Concurrency** | `asyncio.Semaphore(5)` to respect Gemini API rate limits |
| **Real-time progress** | `sse-starlette` + `fetch-event-source` for server-to-client broadcasting with auth |
| **MD5 dedup** | Blob Storage path-based caching avoids re-extracting identical documents |
| **HttpOnly refresh cookie** | Prod-grade XSS protection; survives page refresh without localStorage risk |
| **Auth gate, not flow gate** | `ProtectedRoute` only checks authentication — doesn't enforce page ordering, preserving natural URL navigation for authenticated users |
| **Deterministic ObjectId** | User `_id` derived from identity fields via BLAKE2b for idempotent user creation |
| **Mongo-first delete cascade** | On user deletion: Mongo docs deleted first, blobs second. Orphan blobs are recoverable; dangling user docs are not. |
| **In-memory token blocklist (v1)** | Zero-infra for dev; documented upgrade path to Mongo TTL in [auth.md](auth.md#6-token-blocklist-scaling) |

---

## Sub-Documents

Detailed architecture for specific subsystems. Reference these when working on related tasks.

| Document | Scope | When to reference |
|----------|-------|-------------------|
| [auth.md](auth.md) | JWT tokens, blocklist scaling, RBAC, threat model, admin operations | Any auth/authorization task, token handling, admin user management |
