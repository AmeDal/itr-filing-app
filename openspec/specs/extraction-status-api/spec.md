## ADDED Requirements

### Requirement: Batch Status Retrieval
The system must provide an endpoint to retrieve the current status of all documents associated with a `batch_id`.

#### Scenario: Polling for status
- **WHEN** the frontend requests `GET /api/extract/status/{batch_id}`
- **THEN** it should receive a list of documents with their current status (`queued`, `extracting`, `completed`, `error`) and extracted data (if completed).

### Requirement: Granular Progress Updates
The system must update individual document statuses as they transition through the extraction pipeline.

#### Scenario: Document finishes extraction
- **WHEN** the `llm_service` successfully extracts data from a document
- **THEN** its status in the database should be updated to `completed` and the `extracted_data` field populated.
- **AND** the next status poll should reflect this change.
