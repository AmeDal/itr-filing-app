## MODIFIED Requirements

### Requirement: Authenticated ITR Upload
The ITR upload flow must no longer accept `user_id` as a request parameter; it must derive identity from the authenticated session.

#### Scenario: User uploads document
- **WHEN** the `POST /v1/itr/upload` request is processed
- **THEN** the system must use the `current_user.id` from the JWT for all database and blob storage operations, ignoring any spoofed form fields.
