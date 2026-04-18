## Capability: Blob Storage

### Requirement: Content-Based Deduplication
The system must avoid re-processing documents that have already been parsed by checking a content-hash-based directory in Blob Storage.

#### Scenario: Repeat Upload
- **WHEN** a document with the same MD5 hash already exists in the user's specific Azure storage path and matches the expected page count.
- **THEN** the extraction is skipped, status is marked "Completed (Cached)", and "Force Re-parse" is enabled.

### Requirement: Result Persistence
Every successful page extraction must be saved as an individual JSON file.

#### Scenario: Output Generation
- **WHEN** a page is successfully analyzed by Gemini.
- **THEN** it is saved to Azure Blob at `{user_id}/{AY}/{doc_type}/{md5}/page_{n}.json`.
