## 1. Dependencies & Configuration

- [x] 1.1 Add `pymongo[encryption]>=4.2` to `requirements.txt`
- [x] 1.2 Add `csfle_master_key: str` and `csfle_key_vault_namespace: str` to `settings.py`
- [x] 1.3 Rename `"password"` → `"hashed_password"` in `Settings.get_seed_user_dict()`
- [x] 1.4 Generate a 96-byte master key (base64) and add `CSFLE_MASTER_KEY=<value>` to `.env`

## 2. CryptoService

- [x] 2.1 Create `backend/services/crypto_service.py` with `CryptoService` singleton class
- [x] 2.2 Implement `CryptoService.initialize(mongo_uri, master_key_b64, key_vault_ns)` — creates sync MongoClient, loads master key, creates or retrieves DEK by altName `"itr-password-dek"`
- [x] 2.3 Implement `async CryptoService.encrypt_field(value: str) → Binary` using `asyncio.to_thread()`
- [x] 2.4 Implement `async CryptoService.decrypt_field(ciphertext: Binary) → str` using `asyncio.to_thread()`
- [x] 2.5 Implement `CryptoService.close()` to release the sync client

## 3. Database Integration

- [x] 3.1 In `db.py` `DatabaseManager.initialize()`: call `CryptoService.initialize()` before seeding
- [x] 3.2 In `db.py` `DatabaseManager._seed_admin_user()`: hash then encrypt the seed password; store as `hashed_password` field
- [x] 3.3 In `db.py` `DatabaseManager.close()`: call `CryptoService.close()`

## 4. User Service Integration

- [x] 4.1 In `user_service.py` `create_user()`: encrypt Argon2 hash via `CryptoService.encrypt_field()` before insert; use field name `hashed_password`
- [x] 4.2 In `user_service.py` `login_user()`: decrypt `hashed_password` via `CryptoService.decrypt_field()` before calling `verify_password()`
- [x] 4.3 Remove all references to the old `password` field name in `user_service.py`

## 5. Verification

- [x] 5.1 Start the app and confirm startup logs show CryptoService initialization and DEK creation/reuse
- [x] 5.2 Signup via `/api/users/signup` — confirm `UserResponse` contains no password fields
- [x] 5.3 Inspect the inserted document in Atlas UI — confirm `hashed_password` is encrypted Binary (not readable text)
- [x] 5.4 Login with correct password — confirm success; login with wrong password — confirm failure
