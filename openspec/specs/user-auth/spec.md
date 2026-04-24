## Capability: User Auth

### Requirement: Deterministic User ObjectId Generation
The system must generate a deterministic BSON ObjectId for every user based on normalized core identity fields.

#### Scenario: User provides unique details
- **WHEN** a user provides first name, middle name, last name, PAN, Aadhar, pincode, mobile, email, and password
- **THEN** the system concatenates the identity fields excluding password with `|`
- **AND** normalizes names/email to lowercase, PAN to uppercase, and numeric fields by trimming
- **AND** computes a 12-byte BLAKE2b digest used as the BSON ObjectId bytes.

### Requirement: Secure Unified Signup
The system must allow a user to create a profile by providing all identity details in a single request.

#### Scenario: Valid signup processing
- **WHEN** the signup request is received with valid mandatory fields
- **THEN** the system computes the deterministic ObjectId, checks encrypted PAN/email conflicts, hashes and encrypts the password, encrypts PII fields, and saves the user with an IST `created_at` timestamp.

### Requirement: Strict Input Validation
The system must enforce specific formats for identity fields on the backend and frontend.

- **PAN**: 10 characters, 5 uppercase letters, 4 digits, 1 uppercase letter.
- **Aadhar**: exactly 12 digits.
- **Mobile**: exactly 10 digits.
- **Pincode**: exactly 6 digits.
- **Password**: at least 12 characters with uppercase, lowercase, digit, and one allowed special character.

#### Scenario: User provides malformed identity data
- **WHEN** a user enters malformed identity data or a weak password
- **THEN** the system prevents successful signup and returns field-specific validation errors.

### Requirement: Tokenized Login Response
The system must verify PAN/password credentials and return an access token upon success.

#### Scenario: Successful login
- **WHEN** a user submits valid OAuth2 form credentials using PAN as `username`
- **THEN** the response conforms to `AuthResponse`
- **AND** includes an access token and user summary
- **AND** securely sets the refresh token cookie.
