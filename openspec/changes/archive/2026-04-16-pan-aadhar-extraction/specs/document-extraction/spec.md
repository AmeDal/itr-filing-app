## ADDED Requirements

### Requirement: Extract Document Details via AI
The system SHALL accept a valid image file representing a PAN or Aadhar card and return the extracted details in a structured JSON schema.

#### Scenario: Successful PAN extraction
- **WHEN** a user uploads a valid PAN card image
- **THEN** the system returns structured JSON containing PAN number, Full Name, Father's Name, and DOB.
- **AND** the database remains unmodified.

#### Scenario: Successful Aadhar extraction
- **WHEN** a user uploads a valid Aadhar card image
- **THEN** the system returns structured JSON containing Aadhar number, Full Name, DOB, Gender, and Full Address.
- **AND** the database remains unmodified.
