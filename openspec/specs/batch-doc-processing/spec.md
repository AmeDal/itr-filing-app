## Capability: Batch Document Processing

### Requirement: Multi-file ITR Document Ingestion
The system must allow a single authenticated request to upload multiple ITR-supporting documents for one assessment year and ITR type.

#### Scenario: User uploads required documents
- **WHEN** the user submits files, `doc_types`, `ay`, and `itr_type` to `POST /api/v1/itr/upload`
- **THEN** the system upserts a `filing_attempts` record for the authenticated user and assessment year
- **AND** creates an in-memory processing session
- **AND** returns a `session_id`.

### Requirement: Async Extraction Trigger
The system must initiate document extraction in the background without blocking the ingestion response.

#### Scenario: Background processing starts
- **WHEN** the upload request is accepted
- **THEN** a FastAPI background task starts `ITRProcessingService.process_session`
- **AND** each document is processed independently so one failure does not stop the full session.

### Requirement: Scoped Session Extraction
All sessions and filing attempts must be bound to the authenticated user who initiated the upload.

#### Scenario: User subscribes to session status
- **WHEN** a user requests `GET /api/v1/itr/progress/{session_id}`
- **THEN** the system streams progress only if the session belongs to that authenticated user.
