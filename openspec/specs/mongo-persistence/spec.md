## Capability: Mongo Persistence

### Requirement: Async MongoDB Integration
The system must use PyMongo's native async client for MongoDB request-time database operations.

#### Scenario: Database operation during request
- **WHEN** an API request requires a database read or write
- **THEN** the system awaits the operation using `pymongo.AsyncMongoClient` without blocking the event loop.

### Requirement: CSFLE Sync Boundary Offload
Synchronous CSFLE setup and field encryption/decryption must not block the async event loop.

#### Scenario: Startup crypto initialization
- **WHEN** `DatabaseManager.initialize()` initializes `CryptoService`
- **THEN** synchronous CSFLE setup executes via `asyncio.to_thread`.

#### Scenario: Field encryption/decryption
- **WHEN** sensitive fields are encrypted or decrypted
- **THEN** the synchronous encryption/decryption call executes via `asyncio.to_thread`.

### Requirement: IST Timezone Consistency
Temporal metadata stored in MongoDB must use Indian Standard Time (UTC+5:30).

#### Scenario: Document or user creation
- **WHEN** a new user or filing attempt is inserted
- **THEN** `created_at` is populated with the current IST time.
