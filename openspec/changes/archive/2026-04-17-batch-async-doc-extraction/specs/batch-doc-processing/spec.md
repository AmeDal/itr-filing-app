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
