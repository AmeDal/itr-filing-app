## Capability: ITR Processing

### Requirement: In-Memory Processing Sessions
The system must support ephemeral in-memory processing sessions for ITR document analysis while persisting filing metadata in MongoDB.

#### Scenario: Session initiation
- **WHEN** an authenticated user uploads ITR documents
- **THEN** an in-memory session is created to track document/page extraction state
- **AND** a `filing_attempts` record stores the assessment year, ITR type, and document metadata.

### Requirement: SSE Progress Tracking
The system must provide real-time document processing updates via Server-Sent Events.

#### Scenario: User tracks progress
- **WHEN** a user subscribes to the progress stream for their session
- **THEN** the system pushes updates as documents move from `queued` to `extracting` to `completed` or failed/error.

### Requirement: Owner-Scoped Processing
Processing state and persisted filing records must be scoped to the authenticated user.

#### Scenario: Cross-user session access
- **WHEN** a different authenticated user requests another user's session stream
- **THEN** the system does not stream that session's state.
