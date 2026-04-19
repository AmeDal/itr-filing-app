## ADDED Requirements

### Requirement: Persist filing metadata
The system must store assessment year, ITR type, and document extraction status in MongoDB.

#### Scenario: Successful upload initialization
- **WHEN** a user uploads a batch of documents
- **THEN** a document in `filing_attempts` is created or updated with `is_extraction_complete: false` for each doc.

### Requirement: Live status updates
Extraction progress must be updated in MongoDB after each page.

#### Scenario: Page extraction completion
- **WHEN** a page is successfully saved to blob storage
- **THEN** only the in-memory progress and the DB record for the filing attempt are updated to reflect the new state.
