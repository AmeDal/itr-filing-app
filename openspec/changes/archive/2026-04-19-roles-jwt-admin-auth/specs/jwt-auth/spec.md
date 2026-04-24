## ADDED Requirements

### Requirement: JWT Access Token Issuance
The system must issue a short-lived (30 min) JWT access token upon successful login, containing only minimal identity claims.

#### Scenario: User logs in
- **WHEN** a user provides valid PAN and Password
- **THEN** the system must return an `access_token` containing `sub` (user_id) and `role` claims, signed with HS256.

### Requirement: Refresh Token Cookie
The system must set an HttpOnly, Secure, SameSite=Strict cookie containing a long-lived refresh token.

#### Scenario: User authentication response
- **WHEN** the login or refresh endpoint returns successfully
- **THEN** the browser must receive a `refresh_token` cookie that is inaccessible via JavaScript.

### Requirement: Mandatory Token Rotation
The system must rotate the refresh token on every successful refresh attempt and blocklist the old one.

#### Scenario: User requests refresh
- **WHEN** a valid refresh token cookie is provided to the refresh endpoint
- **THEN** the system must issue a new access/refresh pair and ensure the old refresh token can no longer be used.

### Requirement: Global Auth Dependency
All non-auth endpoints (ITR, Extraction, Admin) must be protected by a mandatory JWT verification layer.

#### Scenario: Unauthenticated request
- **WHEN** a request is made to `/v1/itr/upload` without a valid Bearer token
- **THEN** the system must return a 401 Unauthorized status.
