## Context

The app uses Motor (async MongoDB) on Atlas M0 free tier. Argon2 password hashing is already in place via `passlib` in `backend/security.py`. Hashes are currently stored as plain strings in user documents. Atlas M0 does not support automatic CSFLE (`auto_encryption_opts`), so explicit CSFLE is the only option.

CSFLE requires `pymongo[encryption]` which ships a synchronous `ClientEncryption` API — there is no async equivalent. The Motor async client is used for all other DB operations.

## Goals / Non-Goals

**Goals:**
- Encrypt `hashed_password` at the application layer before any data reaches Atlas
- Use a single Data Encryption Key (DEK), created once at startup and reused
- Store the 96-byte local KMS master key in `.env` (base64-encoded)
- Wrap synchronous `ClientEncryption` calls in `asyncio.to_thread()` for async safety
- Rename field `password` → `hashed_password` throughout for clarity

**Non-Goals:**
- Automatic CSFLE (requires Atlas M9+ or Enterprise)
- Per-user DEKs (adds complexity with no significant benefit for this use case)
- KMS provider integration (AWS/Azure/GCP) — deferred to production
- Migrating existing encrypted documents (user dropped the collection; fresh start)
- Encrypting any field other than `hashed_password`

## Decisions

### D1: Explicit CSFLE (not Automatic)
**Decision**: Use `ClientEncryption.encrypt()` / `decrypt()` explicitly rather than `auto_encryption_opts`.  
**Rationale**: Atlas M0 free tier does not support automatic CSFLE. Explicit encryption achieves identical security — the field is still encrypted before it leaves the app.  
**Alternative considered**: Upgrade Atlas tier — rejected as unnecessary cost for dev.

### D2: Single module `CryptoService` in `services/`
**Decision**: Create `backend/services/crypto_service.py` as a singleton class.  
**Rationale**: Keeps all CSFLE concerns (key vault client, DEK lifecycle, encrypt/decrypt) in one place. Other services import only `CryptoService`. Follows project pattern of services in `backend/services/`.  
**Alternative considered**: Putting code directly in `db.py` — rejected; violates separation of concerns and makes `db.py` too large.

### D3: `asyncio.to_thread()` for sync `ClientEncryption` calls
**Decision**: Wrap all `ClientEncryption` calls in `asyncio.to_thread()`.  
**Rationale**: `ClientEncryption` is synchronous. Calling it directly on the async event loop would block. `to_thread()` is the idiomatic way to run blocking IO in async Python without a separate executor setup.  
**Alternative considered**: `loop.run_in_executor(None, ...)` — equivalent but more verbose; `to_thread` is cleaner in Python 3.9+.

### D4: Random algorithm (not Deterministic)
**Decision**: Use `Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random`.  
**Rationale**: We never query MongoDB by `hashed_password`, so deterministic encryption (which enables equality queries) is unnecessary. Random produces different ciphertext each time, making ciphertext analysis harder.

### D5: DEK identified by `altName`
**Decision**: Create DEK with `key_alt_names=["itr-password-dek"]` and look it up by that name on startup.  
**Rationale**: Ensures idempotent startup — if the DEK already exists in the key vault, it is reused rather than creating a duplicate. The `_id`-based approach would require persisting the DEK ID separately.

## Risks / Trade-offs

- **Master key in `.env`** → If `.env` is compromised, encryption is broken. Mitigation: `.env` is already in `.gitignore`; document KMS migration path for production.
- **Sync `ClientEncryption` in async context** → If key vault is slow, `to_thread()` calls may block the thread pool. Mitigation: Key vault lookup is cached after first call (DEK ID stored in memory); encrypt/decrypt themselves are CPU-bound and fast.
- **Single DEK** → If the DEK is compromised, all encrypted fields are exposed. Mitigation: Acceptable for dev; document per-user DEK rotation path for production.
- **Field rename breaking change** → Existing documents are broken. Mitigation: Already handled — user deleted the collection.

## Migration Plan

1. Generate `CSFLE_MASTER_KEY`: run one-time Python snippet to produce 96 random bytes as base64; store in `.env`
2. Drop `users` collection (already done by user)
3. Deploy updated backend — `CryptoService.initialize()` creates the key vault collection and DEK on first run
4. Seed user is inserted with encrypted `hashed_password` automatically
5. New signups go through the updated `create_user()` path

**Rollback**: Restore old `user_service.py` / `db.py`; drop `encryption.__keyVault` collection; re-insert users (or restore backup).
