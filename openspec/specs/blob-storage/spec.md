## Capability: Blob Storage

### Requirement: Content-Based Page Caching
The system must avoid re-processing pages that already have extraction JSON for the same user, assessment year, document type, and MD5 hash.

#### Scenario: Repeat incomplete upload
- **WHEN** a document with the same MD5 hash already has page JSON files in the user's Azure storage path
- **THEN** the system skips existing pages and processes only missing pages
- **AND** if all expected pages already exist, the document is marked complete.

### Requirement: Completed-Slot Protection
The system must prevent accidental replacement of already completed filing documents.

#### Scenario: Uploading over a completed document
- **WHEN** a user uploads a document type already marked complete for the filing attempt
- **THEN** the upload request is rejected
- **AND** the user must delete the completed document slot from filing history before uploading a replacement.

### Requirement: Result Persistence
Every successful page extraction must be saved as an individual JSON file.

#### Scenario: Output generation
- **WHEN** a page is successfully analyzed by Gemini
- **THEN** it is saved to Azure Blob at `{user_id}/{AY}/{doc_type}/{md5}/page_{n}.json`.
