## ADDED Requirements

### Requirement: CSFLE master key loading
The application SHALL load a 96-byte master key from the `CSFLE_MASTER_KEY` environment variable (base64-encoded) on startup. If the key is absent or invalid, startup SHALL fail with a clear error message.

#### Scenario: Valid master key present
- **WHEN** `CSFLE_MASTER_KEY` is set to a valid base64 string decoding to exactly 96 bytes
- **THEN** `CryptoService.initialize()` completes without error and the key is stored in memory

#### Scenario: Master key missing
- **WHEN** `CSFLE_MASTER_KEY` is empty or not set in `.env`
- **THEN** application startup raises `ValueError` with message indicating the key is required

#### Scenario: Master key wrong length
- **WHEN** `CSFLE_MASTER_KEY` decodes to a byte string that is not exactly 96 bytes
- **THEN** application startup raises `ValueError` indicating the expected length

---

### Requirement: Data Encryption Key (DEK) lifecycle
The system SHALL create or retrieve a single DEK identified by altName `"itr-password-dek"` in the `encryption.__keyVault` collection on startup. DEK creation SHALL be idempotent.

#### Scenario: First startup — DEK does not exist
- **WHEN** no DEK with altName `"itr-password-dek"` exists in the key vault
- **THEN** `CryptoService.initialize()` creates a new DEK and caches its ID

#### Scenario: Subsequent startup — DEK already exists
- **WHEN** a DEK with altName `"itr-password-dek"` already exists in the key vault
- **THEN** `CryptoService.initialize()` retrieves the existing DEK ID and caches it (no duplicate created)

---

### Requirement: Field encryption on write
The system SHALL encrypt the Argon2 `hashed_password` string using `AEAD_AES_256_CBC_HMAC_SHA_512-Random` before inserting or updating any user document in MongoDB.

#### Scenario: User created via signup
- **WHEN** `create_user()` is called with a valid plaintext password
- **THEN** the password is first hashed with Argon2, then the hash is encrypted, and the resulting Binary is stored in the `hashed_password` field; no plaintext hash is stored

#### Scenario: Seed user inserted at startup
- **WHEN** the seed user does not yet exist and `_seed_admin_user()` runs
- **THEN** the seed password is hashed then encrypted before insertion into MongoDB

#### Scenario: Inspecting MongoDB document directly
- **WHEN** a document in the `users` collection is read without decryption (e.g., via Atlas UI)
- **THEN** the `hashed_password` field contains a BSON Binary subtype 6 value (not the Argon2 hash string)

---

### Requirement: Field decryption on read
The system SHALL decrypt the `hashed_password` Binary field before passing it to `verify_password()` during login.

#### Scenario: Login with correct password
- **WHEN** `login_user()` is called with a valid PAN and correct plaintext password
- **THEN** `hashed_password` is decrypted to the Argon2 hash, `verify_password()` returns True, and `UserResponse` is returned

#### Scenario: Login with wrong password
- **WHEN** `login_user()` is called with a valid PAN and incorrect plaintext password
- **THEN** `hashed_password` is decrypted, `verify_password()` returns False, and `None` is returned

---

### Requirement: Password field not exposed in API responses
The system SHALL never include `password` or `hashed_password` in any API response to the client.

#### Scenario: Signup response
- **WHEN** `POST /api/users/signup` succeeds
- **THEN** the JSON response contains user identity fields but no `password` or `hashed_password` key

#### Scenario: Login response
- **WHEN** `POST /api/users/login` succeeds
- **THEN** the JSON response contains user identity fields but no `password` or `hashed_password` key
