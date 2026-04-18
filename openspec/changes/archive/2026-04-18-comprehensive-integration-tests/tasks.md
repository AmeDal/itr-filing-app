## 1. Environment & Setup

- [x] 1.1 Add `pytest`, `pytest-asyncio`, and `httpx` dependencies to `requirements.txt`.
- [x] 1.2 Establish `backend/tests/integration/` package structure.
- [x] 1.3 Create `.env.test` ensuring `mongo_db_name=AmeDal_test` and providing a dedicated deterministic `CSFLE_MASTER_KEY` generated solely for testing.

## 2. Global Fixtures (`conftest.py`)

- [x] 2.1 Initialize `event_loop` async fixture overriding the default.
- [x] 2.2 Create `db_init` async fixture that forces settings to load from `.env.test`, verifying the DB name ends with `_test`, then invokes `DatabaseManager.initialize()`.
- [x] 2.3 Create `db_cleanup` async fixture hooked to tests causing `delete_many({})` across all collections (users, documents) to guarantee test isolation. 
- [x] 2.4 Create `async_client` fixture returning `httpx.AsyncClient` bound to `backend.main:app` with base URL `http://test`.

## 3. CSFLE Secure Auth & Identity Integrations

- [x] 3.1 In `test_auth.py`, write `test_signup_integration` that uses `async_client` to `POST /api/users/signup` with full schema data, asserting the response is 200 OK.
- [x] 3.2 Add raw MongoDB assertion logically inside `test_signup_integration` querying Motor `db.users` directly to verify `pan_number` and `password` are written as `bson.binary.Binary` entities on disk.
- [x] 3.3 Write `test_login_integration` proving that `POST /api/users/login` successfully interacts with the database to execute deterministic BSON comparisons and complete user authentication.

## 4. Extraction Routing Pipeline

- [x] 4.1 In `test_extraction.py`, write `test_malformed_document_extraction` testing the `POST /api/documents/extract/stream` router logic with a mock non-pdf binary payload.
- [x] 4.2 Validate the boundary stream behavior asserting that FastAPI responds properly without 500 crashes and successfully relays the HTTP streaming chunks identifying the bad input document back to `AsyncClient`.
