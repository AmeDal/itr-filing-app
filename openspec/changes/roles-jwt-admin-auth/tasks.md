## 1. Backend: JWT Core & Foundations

- [x] 1.1 Add `PyJWT[crypto]` to `requirements.txt`.
- [x] 1.2 Extend `settings.py` with JWT settings (`jwt_secret`, `access_token_expire_minutes`, etc.).
- [x] 1.3 Implement `backend/services/token_blocklist.py` (in-memory v1).
- [x] 1.4 Create `backend/auth_deps.py` with `OAuth2PasswordBearer`, `get_current_user`, and `require_admin`.
- [x] 1.5 Create core auth service logic: `create_access_token`, `create_refresh_token`, and token decoding.
- [x] 1.6 Update `user_service.py` with typed exceptions, `is_active` validation, and safe `decrypt_user_doc` (skipping password).
- [x] 1.7 Add `role` and `is_active` to `db.py` seed logic and `UserResponse` schema.

## 2. Backend: Secure Existing Routers

- [x] 2.1 Update `user_router.py`: return `AuthResponse` from login (with HttpOnly refresh cookie); add `/refresh`, `/logout`, and `/me` endpoints.
- [x] 2.2 Protect `extraction_router.py`: add `get_current_user` dependency; implement batch scoping by `created_by_user_id`.
- [x] 2.3 Protect `itr_router.py`: remove `user_id` from Form parameters; derive identity from `current_user.id`; bind session ownership.

## 3. Frontend: Authentication State & UX

- [x] 3.1 Create `AuthContext.jsx` for memory-only token storage and silent refresh.
- [x] 3.2 Create `ProtectedRoute.jsx` as an auth gate.
- [x] 3.3 Update `api.js`: implement `fetchWithAuth`, 401 interceptor, and SSE with Bearer headers (`fetch-event-source`).
- [x] 3.4 Create `AppLayout.jsx` and `UserMenu.jsx`.
- [x] 3.5 Update `App.jsx` for routing and `AuthPage.jsx` for context integration and auto-navigation.

## 4. Administrative Management

- [x] 4.1 Create `admin_router.py` with full PII visibility, role management, and last-admin guard.
- [x] 4.2 Implement `user_deletion_service.py` with Mongo/Blob cascade deletion.
- [x] 4.3 Add `force-reset-password` endpoint to admin router.
- [x] 4.4 Create `AdminUsersPage.jsx` with table actions and modals.

## 5. Hardening & Finalization

- [ ] 5.1 Implement integration tests in `backend/tests/integration/test_auth.py`.
- [ ] 5.2 Configure project-wide CORS to specific origins.
- [ ] 5.3 Update `AGENTS.md` and project documentation.
