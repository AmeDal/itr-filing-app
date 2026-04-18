## Why

The `users` collection currently stores Argon2 password hashes in plaintext MongoDB documents. If an attacker gains Atlas credentials or performs a database dump, they can attempt offline brute-force attacks against the hashes. Client-Side Field Level Encryption (CSFLE) eliminates this risk by encrypting the `hashed_password` field **before** it leaves the application — Atlas never sees the plaintext hash, only encrypted Binary data.

## What Changes

- Add `pymongo[encryption]` dependency (installs `pymongocrypt` + `libmongocrypt`)
- **BREAKING**: Rename field `password` → `hashed_password` in `users` collection documents
- New `CryptoService` singleton to manage explicit CSFLE lifecycle (key vault, DEK, encrypt/decrypt)
- `db.py` initializes `CryptoService` on startup; encrypts seed user's hashed password
- `user_service.py` encrypts hashed password on create; decrypts before verify on login
- `settings.py` adds `csfle_master_key` (base64 96-byte) and `csfle_key_vault_namespace` config
- `.env` gets a generated `CSFLE_MASTER_KEY` value

## Capabilities

### New Capabilities
- `csfle-password-encryption`: Client-side encryption of `hashed_password` field in MongoDB using explicit CSFLE with a local KMS master key and per-deployment Data Encryption Key (DEK). Covers key management, field encryption on write, and field decryption on read.

### Modified Capabilities
- (none — password hashing behavior is unchanged; this adds an encryption layer around existing Argon2 output)

## Impact

- **`requirements.txt`**: New dependency `pymongo[encryption]>=4.2`
- **`backend/settings.py`**: Two new config fields; seed dict renames `password` key
- **`backend/services/crypto_service.py`**: New file
- **`backend/db.py`**: `initialize()` and `close()` integrate `CryptoService`; seed uses `hashed_password`
- **`backend/services/user_service.py`**: `create_user()` encrypts; `login_user()` decrypts
- **`.env`**: New `CSFLE_MASTER_KEY` variable
- **Atlas `encryption.__keyVault` collection**: Created automatically at startup to hold the DEK
- **Breaking**: Existing `users` documents are invalid — collection must be dropped before first run
