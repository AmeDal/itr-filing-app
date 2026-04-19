## MODIFIED Requirements

### Requirement: User-Scoped Batch Initialization
Each batch extraction must record the identity of the user who created it to ensure secure status polling.

#### Scenario: User checks batch status
- **WHEN** a user polls `/v1/extract/status/{batch_id}`
- **THEN** the system must only return results if the `batch_id` is linked to the authenticated user's ID.
