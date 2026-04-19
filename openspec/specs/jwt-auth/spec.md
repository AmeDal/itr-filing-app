## ADDED Requirements

### Requirement: Refresh Token Rotation
The system must support a stateless, rotating refresh token mechanism to maintain long-lived sessions securely.

#### Scenario: Token rotation initiated
- **WHEN** a valid refresh token cookie is provided to the refresh endpoint
- **THEN** the system must issue a new access/refresh pair and ensure the old refresh token is revoked/blocked.

### Requirement: Global Auth Dependency
All non-auth endpoints must be protected by a mandatory JWT verification layer.

#### Scenario: Unauthenticated request
- **WHEN** a request is made to a protected endpoint (e.g. `/v1/itr/upload`) without a valid Bearer token
- **THEN** the system must return a 401 Unauthorized status.
