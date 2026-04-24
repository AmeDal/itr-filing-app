## Capability: Admin Management

### Requirement: Admin Role-Based Access Control (RBAC)
The system must distinguish between `admin` and `user` roles and restrict user-management APIs to admins.

#### Scenario: Admin views all users
- **WHEN** an authenticated user with role `admin` requests `GET /api/v1/admin/users`
- **THEN** the system returns a paginated list of users with decrypted PII fields except `password`
- **AND** non-admin users receive `403`.

### Requirement: User Lifecycle Management
Administrators must be able to change a user's role and active status while preserving the last active admin.

#### Scenario: Deactivating a user
- **WHEN** an admin sets a user's `is_active` status to `false`
- **THEN** that user is prevented from logging in or using existing access tokens on subsequent protected requests
- **AND** the system prevents self-deactivation and deactivation/demotion of the last active admin.

### Requirement: Administrative Identity Deletion
The system must support cascade hard-delete for user profiles and filing data.

#### Scenario: Cascade delete initiated
- **WHEN** an admin deletes a user profile
- **THEN** the system deletes that user's `filing_attempts`, deletes blobs under the user's Azure prefix, and deletes the user profile
- **AND** the system prevents self-deletion and deletion of the last active admin
- **AND** the cascade is sequential rather than a Mongo transaction.

### Requirement: Administrative Password Reset
Admins must be able to force-reset a user's password using the same password-strength policy as signup.

#### Scenario: Admin resets password
- **WHEN** an admin submits a valid new password to `POST /api/v1/admin/users/{user_id}/reset-password`
- **THEN** the password is Argon2-hashed off the event loop, encrypted with random CSFLE, and stored in `users.password`.
