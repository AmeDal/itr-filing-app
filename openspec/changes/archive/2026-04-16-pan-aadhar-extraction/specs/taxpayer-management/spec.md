## ADDED Requirements

### Requirement: Create Taxpayer
The system SHALL create a new taxpayer record when provided with verified PAN details.

#### Scenario: Save verified PAN
- **WHEN** an API client submits verified JSON containing PAN details
- **THEN** the system creates a new entry in the 'taxpayers' table
- **AND** the 'taxpayers' table enforces PAN as the primary, unique identifier.

### Requirement: Link Aadhar to Taxpayer
The system SHALL update an existing taxpayer record with Aadhar details based on the PAN.

#### Scenario: Successful Aadhar linking
- **WHEN** an API client submits verified JSON containing Aadhar details for an existing PAN
- **THEN** the system updates the corresponding taxpayer record with the aadhar_number, address, and gender.

#### Scenario: Linking to non-existent PAN
- **WHEN** an API client submits Aadhar details for a PAN that doesn't exist
- **THEN** the system returns a 404 Not Found error.
