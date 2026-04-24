## ADDED Requirements

### Requirement: In-Memory Processing Sessions
The system must support ephemeral, in-memory processing sessions for ITR document analysis that do not persist to long-term storage until finalized.

#### Scenario: Session initiation
- **WHEN** a user uploads ITR documents
- **THEN** an in-memory session must be created to track the state of individual document extractions.

### Requirement: SSE Progress Tracking
The system must provide real-time updates on document processing status via Server-Sent Events (SSE).

#### Scenario: User tracks progress
- **WHEN** a user subscribes to the progress stream for their session
- **THEN** the system must push updates as each document moves from `queued` to `extracting` to `completed`.
