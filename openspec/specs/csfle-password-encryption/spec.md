## Capability: CSFLE Field Encryption

### Requirement: CSFLE Master Key Loading
The application SHALL load a 96-byte master key from the `CSFLE_MASTER_KEY` environment variable as a base64-encoded value.

#### Scenario: Valid master key present
- **WHEN** `CSFLE_MASTER_KEY` decodes to exactly 96 bytes
- **THEN** `CryptoService.initialize()` completes and creates a `ClientEncryption` instance.

#### Scenario: Master key missing or invalid
- **WHEN** `CSFLE_MASTER_KEY` is empty, not base64, or not exactly 96 bytes
- **THEN** startup raises a clear `ValueError`.

### Requirement: Data Encryption Key (DEK) Lifecycle
The system SHALL create or retrieve a single DEK identified by altName `itr-password-dek` in the configured key vault namespace.

#### Scenario: First startup
- **WHEN** no DEK with altName `itr-password-dek` exists
- **THEN** `CryptoService.initialize()` creates it and caches its ID.

#### Scenario: Subsequent startup
- **WHEN** the DEK already exists
- **THEN** `CryptoService.initialize()` reuses it without creating a duplicate.

### Requirement: Field Encryption on Write
The system SHALL encrypt sensitive user fields before inserting or updating user documents in MongoDB.

#### Scenario: User created via signup
- **WHEN** `create_user()` is called with a valid plaintext password
- **THEN** the password is Argon2-hashed off the event loop
- **AND** the hash is encrypted with random CSFLE into the `password` field
- **AND** identity fields, `role`, and `is_active` are encrypted deterministically for exact-match queries.

#### Scenario: Seed user inserted at startup
- **WHEN** `_seed_admin_user()` creates the seed user
- **THEN** the seed password is hashed and encrypted before insertion.

### Requirement: Field Decryption on Read
The system SHALL decrypt encrypted fields before validation or API serialization.

#### Scenario: Login with correct password
- **WHEN** `login_user()` finds a user by deterministically encrypted PAN
- **THEN** `password` is decrypted to the Argon2 hash and verified off the event loop.

#### Scenario: Protected request
- **WHEN** `get_current_user()` loads a user document
- **THEN** encrypted `is_active` is decrypted before allowing access.

### Requirement: Password Field Not Exposed
The system SHALL never include `password` in API responses.

#### Scenario: Signup or login response
- **WHEN** a user receives a profile or auth response
- **THEN** the JSON response contains no `password` key.
