## Capability: Async Processing Engine

### Requirement: In-Memory Processing
All document processing (PDF to image conversion and Gemini API payload preparation) MUST occur strictly in RAM. No temporary files or disk-based caching of source documents is allowed.

#### Scenario: Successful PDF Extraction
- **WHEN** a valid PDF is uploaded.
- **THEN** it is converted into 200 DPI PNG images in-memory and processed in concurrent batches of 5.

### Requirement: Rate-Limit Resilience
The engine must gracefully handle 429 errors from the Gemini API by implementing an exponential backoff retry mechanism (15s, 30s, 45s).

#### Scenario: Temporary Rate Limit
- **WHEN** Gemini returns a 429 status code.
- **THEN** the specific page task waits for the calculated delay and retries, up to 3 times total.

### Requirement: Page-Level Tracking
Progress must be recorded at the individual page level to support partial retries.

#### Scenario: Partial Failure
- **WHEN** 1 out of 10 pages fails after all retries.
- **THEN** the document is marked as "Failed", and the UI enables a "Retry" button that only re-queues the failed page.
