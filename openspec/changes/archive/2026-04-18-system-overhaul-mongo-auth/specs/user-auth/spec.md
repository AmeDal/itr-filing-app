## ADDED Requirements

### Requirement: Deterministic User OID Generation
The system must generate a unique, deterministic 64-character hex ID (SHA-256) for every user based on their core identity fields.

#### Scenario: User provides unique details
- **WHEN** a user provides their First Name, Middle Name, Last Name, PAN, Aadhar, Pincode, Mobile, Email, and Password
- **THEN** the system should concatenate these identity fields (excluding password) with a "|" delimiter, convert to lowercase/uppercase as specified, and return the SHA-256 hash.

### Requirement: Secure Unified Signup
The system must allow a user to create a profile by Providing all identity details in a single atomic operation.

#### Scenario: Valid signup processing
- **WHEN** the signup request is received with all 9 mandatory fields (including password)
- **THEN** the system should compute the OID, check for existing PAN/Email conflicts, and save the record to MongoDB with a `created_at` timestamp in IST.

### Requirement: Strict Input Validation
The system must enforce specific formats for identity fields on both the frontend and backend.

- **PAN**: 10 characters, Alphanumeric (5 letters, 4 digits, 1 letter).
- **Aadhar**: 12 digits precisely.
- **Mobile**: 10 digits precisely.
- **Pincode**: 6 digits precisely.
- **Password**: Minimum 8 characters.

#### Scenario: User provides malformed identity data
- **WHEN** a user enters a 9-character PAN or an 11-digit Aadhar number
- **THEN** the system must prevent submission and display a field-specific error message.

### Requirement: Simple PAN-Password Login
The system must verify a user's existence based on the combination of their PAN and Password.

#### Scenario: Successful login
- **WHEN** a user provides a valid PAN and their matching password
- **THEN** the system should return the full user profile with a 200 OK status.
