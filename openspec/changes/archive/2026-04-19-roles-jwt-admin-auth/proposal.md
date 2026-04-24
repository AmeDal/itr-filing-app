## Why

Currently, the ITR Filing App lacks a robust authentication mechanism. Login and signup exist only as stubs returning user data without tokens, and sensitive operations like ITR uploads and document extractions are unprotected. This change introduces JWT-based authentication with role-based access control (admin/user) to secure the API surface, protect user data, and enable administrative management of users and their sensitive documents.

## What Changes

- Introduction of a JWT-based authentication system using `PyJWT`.
- Implementation of Access and Refresh tokens with mandatory rotation.
- Role-based Access Control (RBAC) with `admin` and `user` roles.
- Hardened API surface: protecting extraction and ITR processing endpoints.
- Ownership binding: ITR sessions and document batches will be tied to the authenticated user's ID.
- Admin dashboard: user management UI for listing, updating role/status, force-resetting passwords, and cascade-deleting users (including cloud blobs).
- Frontend integration: AuthContext, route guards, and fetch-based SSE to support Bearer tokens.

## Capabilities

### New Capabilities
- `jwt-auth`: Core authentication and authorization logic, including token issuance, verification, and blocklisting.
- `admin-mgmt`: Administrative tools to manage user accounts, roles, and data cleanup.

### Modified Capabilities
- `itr-processing`: Binding sessions to users and requiring auth headers for progress tracking.
- `batch-extraction`: Scoping document extraction batches to the creating user.

## Impact

- **Backend**: New dependencies (`PyJWT`), new auth middleware/dependencies, modified routers (`itr`, `extraction`), and a new `admin` router.
- **Frontend**: New `AuthContext`, updated `api.js`, updated routing logic, and a new `AdminUsersPage`.
- **Database**: Extended `users` collection schema; new `documents` fields for ownership.
- **Storage**: Azure Blob Storage paths now derived strictly from authenticated user context.
