## Capability: Upload Flow

### Requirement: Required Document Upload
The UI must require the core ITR documents before allowing upload and processing.

#### Scenario: Missing required document
- **WHEN** a user attempts to proceed without Form 26AS, AIS, TIS, or at least one Bank Statement
- **THEN** the "Upload & Process" button remains disabled
- **AND** the UI indicates required documents are missing.

### Requirement: Form 16 Warning
A secondary validation check must occur if Form 16 is omitted.

#### Scenario: Form 16 omission
- **WHEN** the user proceeds without a Form 16
- **THEN** a modal warning is displayed
- **AND** the user must choose "Confirm and Proceed" before upload continues.

### Requirement: Live Feedback
The progress dashboard must update in real time as pages are processed.

#### Scenario: Real-time update
- **WHEN** any page extraction completes successfully
- **THEN** an SSE message is received by the frontend
- **AND** the progress bar/text for that document updates.
