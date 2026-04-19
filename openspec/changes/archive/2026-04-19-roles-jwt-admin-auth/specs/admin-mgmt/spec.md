## ADDED Requirements

### Requirement: Role-Based Access Control (RBAC)
The system must distinguish between `admin` and `user` roles for specific endpoint permissions.

#### Scenario: Non-admin access to admin endpoint
- **WHEN** a user with the `user` role attempts to GET `/api/v1/admin/users`
- **THEN** the system must return a 403 Forbidden status.

### Requirement: Admin Cascade User Deletion
The system must provide an admin-only mechanism to permanently delete a user and all their associated data across Mongo and Cloud storage.

#### Scenario: Admin deletes a user account
- **WHEN** an admin requests deletion of user_id X
- **THEN** the system must delete the user doc, all associated documents/batches, and all blobs with the prefix `X/AY-...`.

### Requirement: Admin Force Password Reset
The system must allow an admin to set a new password for any user without knowledge of the current one.

#### Scenario: Admin resets user password
- **WHEN** an admin provides a new validated password for user X
- **THEN** the system must update the user's record and invalidate all their current active sessions/tokens.
