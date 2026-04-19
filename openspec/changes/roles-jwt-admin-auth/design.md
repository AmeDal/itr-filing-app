## Context

The current application lacks authentication and authorization. All endpoints are public, and user identity is spoofable via request parameters (e.g., `user_id` in Form data). MongoDB and Azure Blob storage paths are not securely isolated.

## Goals / Non-Goals

**Goals:**
- Implement secure, stateless JWT authentication.
- Implement RBAC (admin/user) with `admin` having management capabilities.
- Bind all sensitive resources (sessions, batches, blobs) to the authenticated user identity.
- Provide a prod-grade refresh token mechanism using HttpOnly cookies.
- Enable administrative user management (force reset, cascade delete).

**Non-Goals:**
- Real-time rate limiting (deferred to v2).
- Email service integration for invites/resets (admin handles manually).
- Multi-factor authentication (MFA).

## Decisions

- **Token Library**: Use `PyJWT` for its active maintenance and robustness.
- **Transport**: Hybrid model—access token in JSON (memory-only in React), refresh token in `HttpOnly; Secure; SameSite=Strict` cookie to prevent XSS/CSRF compromise.
- **Blocklist**: In-memory `jti` blocklist for single-process development, with a documented path to MongoDB TTL implementation for production workers.
- **Ownership Enforcement**: Remove all `user_id` type parameters from user-facing forms; derive identity exclusively from the `sub` claim in the verified access JWT.
- **Admin Visibility**: Admin users decrypted identity fields (PII) are visible for management purposes, but password hashes remain strictly inaccessible.
- **Cascade Delete**: Order is Mongo deletion first, then idempotent Cloud Blob deletion to ensure data integrity.

## Risks / Trade-offs

- **Memory-only Access Tokens**: Page refreshes require a silent refresh call to restore state. This increases API load slightly but enhances security.
- **CORS Constraints**: Switching to `credentials: include` for cookies requires strict origin matching instead of `allow_origins="*"`, which might complicate local development if not configured correctly.
- **In-Memory Blocklist**: If the server restarts, all revocations are lost. Acceptable for dev/v1 as tokens are short-lived.
