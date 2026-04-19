## ADDED Requirements

### Requirement: Admin Role-Based Access Control (RBAC)
The system must distinguish between "admin" and "user" roles, granting exclusive management capabilities to admins.

#### Scenario: Admin views all users
- **WHEN** an authenticated user with the "admin" role requests the user list
- **THEN** the system must decrypt all PII fields (except password) and return the full registry.

### Requirement: User Lifecycle Management
Administrators must be able to toggle user status and modify roles.

#### Scenario: Deactivating a user
- **WHEN** an admin sets a user's `is_active` status to `false`
- **THEN** that user must be prevented from logging in or using their existing access tokens.

### Requirement: Administrative Identity Deletion
The system must support a cascade "hard delete" for users, removing all database records and associated blob storage extractions.

#### Scenario: Cascade delete initiated
- **WHEN** an admin deletes a user profile
- **THEN** the system must atomically remove the user record, all associated documents, and delete all related blobs from Azure Storage.
