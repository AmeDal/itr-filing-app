## Capability: Extraction Status API

### Requirement: Real-Time Session Status
The system must provide a Server-Sent Events endpoint for the current status of an in-memory ITR processing session.

#### Scenario: Streaming progress
- **WHEN** the frontend requests `GET /api/v1/itr/progress/{session_id}` with a valid Bearer token
- **THEN** it receives session state containing each document's queued/extracting/completed/failed status and page counts
- **AND** events are streamed only to the session owner.

### Requirement: Persistent Filing Status
The system must provide persistent filing history endpoints after or during extraction.

#### Scenario: Reading filing history
- **WHEN** the frontend requests `GET /api/v1/filing/history`
- **THEN** it receives the authenticated user's filing attempts and document completion flags.

### Requirement: Granular Progress Updates
The system must update individual document status as pages transition through the extraction pipeline.

#### Scenario: Document finishes extraction
- **WHEN** all expected pages for a document are complete
- **THEN** `filing_attempts.documents[].is_extraction_complete` is updated to `true`
- **AND** the next SSE event and filing-history request reflect completion.
