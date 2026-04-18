## ADDED Requirements

### Requirement: Pytest Async Integration Testing Framework
The application MUST include a global pytest configuration `conftest.py` that sets up and tears down an isolated testing sandbox on backend startups for HTTP requests.

#### Scenario: Running the Test Suite
- **WHEN** the test suite executes
- **THEN** it must use a test-specific environment (`AmeDal_test` db, static `.env.test` file) and cleanly initialize/seed `DatabaseManager` before yielding an `httpx.AsyncClient` tied to the FastAPI `app`.

### Requirement: E2E User identity & Encryption Flow 
Integration tests MUST verify the end-to-end functionality of CSFLE encryption dynamically through the API router endpoints.

#### Scenario: User Signup & Database Integrity Verification
- **WHEN** a valid `POST /api/users/signup` request is sent via `AsyncClient`
- **THEN** the API returns a 200 HTTP response.
- **THEN** a literal `pymongo` query against the raw `AmeDal_test` MongoDB collection MUST prove that `pan_number` and `password` are `bson.binary.Binary` entities, thereby proving encryption works dynamically.

#### Scenario: User Login & Decryption Success
- **WHEN** the newly registered user executes a `POST /api/users/login` with their plaintext credentials
- **THEN** the response is 200 OK
- **THEN** it validates that the internal query by deterministic `pan_number` binary works effectively against motor.

### Requirement: Parallel Document Extraction
Integration tests MUST assert the real-world async throughput handling of the `POST /api/documents/extract/stream` endpoint without mocking external API errors.

#### Scenario: Handling Malformed Documents
- **WHEN** an invalid or encrypted PDF is uploaded
- **THEN** the API handles it without crashing the process, returning appropriate error responses directly to the `AsyncClient` verifying `StreamingResponse` yields are structurally correct strings formatted as json chunks.
