## Capability: Async Processing Engine

### Requirement: In-Memory Processing
All uploaded source-document processing MUST occur in RAM. Source PDFs and uploaded files must not be written to temporary files or disk-based caches.

#### Scenario: Successful PDF extraction
- **WHEN** a valid PDF is uploaded through `POST /api/v1/itr/upload`
- **THEN** PyMuPDF page-count and rasterization work executes off the event-loop thread
- **AND** missing pages are rendered into 200 DPI PNG bytes in memory
- **AND** page extraction tasks are processed with a concurrency limit of 5.

### Requirement: Rate-Limit Resilience
The engine must gracefully handle Gemini 429 errors by using exponential backoff retry delays.

#### Scenario: Temporary rate limit
- **WHEN** Gemini returns a 429 status code
- **THEN** the specific page task waits for the calculated delay and retries, up to 3 times total.

### Requirement: Page-Level Tracking
Progress must be recorded at the individual page level in the in-memory `SessionManager` state.

#### Scenario: Partial failure
- **WHEN** one page fails while other pages succeed
- **THEN** successful page JSON files remain persisted in Blob Storage
- **AND** the affected document status is reflected as failed/error in the SSE session state
- **AND** the orchestrator logs gathered exceptions without preventing other documents from finishing.
