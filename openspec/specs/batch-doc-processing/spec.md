## ADDED Requirements

### Requirement: Multi-file Batch Ingestion
The system must allow a single request to upload multiple document files (PAN, Aadhar, etc.) for processing.

#### Scenario: User uploads two documents
- **WHEN** the user selects a PAN image and an Aadhar PDF and clicks "Process All"
- **THEN** the system should create entries for both documents in the database with status `queued` and return a unique `batch_id`.

### Requirement: Async Extraction Trigger
The system must initiate document extraction in the background without blocking the ingestion response.

#### Scenario: Background processing starts
- **WHEN** the batch ingestion request is successful
- **THEN** background tasks should be spawned to process each document using the `llm_service`.

### Requirement: Scoped Batch Extraction
All document batches and their constituent documents must be bound to the authenticated user who initiated the upload.

#### Scenario: User checks batch status
- **WHEN** a user requests the status of a `batch_id`
- **THEN** the system must only return results if the batch was created by that specific user, ensuring cross-user data isolation.
