## Capability: JWT Auth

### Requirement: Refresh Token Rotation
The system must support a rotating refresh token mechanism to maintain sessions securely.

#### Scenario: Token rotation initiated
- **WHEN** a valid refresh token cookie is provided to `POST /api/v1/users/refresh`
- **THEN** the system issues a new access/refresh pair
- **AND** revokes the old refresh token `jti` in the in-memory blocklist.

### Requirement: Protected API Dependencies
All non-auth API endpoints must be protected by JWT verification and active-user checks.

#### Scenario: Unauthenticated request
- **WHEN** a request is made to a protected endpoint such as `POST /api/v1/itr/upload` without a valid Bearer token
- **THEN** the system returns `401 Unauthorized`.

#### Scenario: Deactivated user request
- **WHEN** a token belongs to a user whose encrypted `is_active` value decrypts to false
- **THEN** the system returns `403 Forbidden`.

### Requirement: Admin-Only API Dependencies
Admin APIs must require both a valid access token and `role == "admin"`.

#### Scenario: Non-admin admin request
- **WHEN** a user token calls `GET /api/v1/admin/users`
- **THEN** the system returns `403 Forbidden`.
