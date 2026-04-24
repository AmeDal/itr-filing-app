## ADDED Requirements

### Requirement: Skip already extracted pages
If the same file is re-uploaded for an incomplete document, only missing pages should be processed.

#### Scenario: Resuming interrupted extraction
- **WHEN** a user uploads a file with the same MD5 hash as a previously interrupted one
- **THEN** the system identifies missing page JSONs in blob storage and only triggers Gemini for those pages.

### Requirement: Handle file replacement
If a different file is uploaded for an existing document slot, the old data must be purged.

#### Scenario: Replacing a document
- **WHEN** a user uploads a file with a DIFFERENT MD5 hash for an existing document slot
- **THEN** the old blob folder for that slot is deleted and extraction starts from scratch.
