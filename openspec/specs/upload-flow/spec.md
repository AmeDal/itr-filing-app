## Capability: Upload Flow

### Requirement: Sequential Stepped Upload
The UI must enforce a specific sequence for document collection, ensuring users don't skip required documents (26AS, AIS, TIS, Bank Statements) without explicit confirmation where allowed.

#### Scenario: Missing Required Document
- **WHEN** a user attempts to proceed without uploading Form 26AS.
- **THEN** the "Continue" button remains disabled and an indicator highlights the missing requirement.

### Requirement: Form 16 Warning
A secondary validation check must occur if Form 16 is omitted, as it is critical for accurate filing.

#### Scenario: Form 16 Omission
- **WHEN** the user proceeds without a Form 16.
- **THEN** an unmissable modal warning is displayed, requiring a "Confirm and Proceed" action.

### Requirement: Live Feedback
The progress dashboard must update in real-time as pages are processed, without requiring a page refresh.

#### Scenario: Real-time Update
- **WHEN** any page extraction completes successfully.
- **THEN** an SSE message is received by the frontend, and the progress bar/text for that document updates instantly.
