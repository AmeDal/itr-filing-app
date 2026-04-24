## MODIFIED Requirements

### Requirement: Sequential Stepped Upload
The UI must enforce a specific sequence for document collection, ensuring users don't skip required documents (26AS, AIS, TIS, Bank Statements) without explicit confirmation where allowed. The UI SHALL maintain high contrast and readability in both `light` and `dark` themes.

#### Scenario: Missing Required Document
- **WHEN** a user attempts to proceed without uploading Form 26AS.
- **THEN** the "Continue" button remains disabled and an indicator highlights the missing requirement.
- **AND** the error states and disabled buttons SHALL remain clearly distinguishable in both themes.

### Requirement: Live Feedback
The progress dashboard must update in real-time as pages are processed, without requiring a page refresh. The progress visuals SHALL be theme-aware.

#### Scenario: Real-time Update
- **WHEN** any page extraction completes successfully.
- **THEN** an SSE message is received by the frontend, and the progress bar/text for that document updates instantly.
- **AND** the progress bar colors SHALL use semantic tokens that adapt to the current theme.
