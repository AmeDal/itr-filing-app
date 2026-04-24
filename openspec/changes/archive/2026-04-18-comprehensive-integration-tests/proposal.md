## Why

The application has recently undergone major architectural shifts, including moving from SQLite to Async MongoDB, and adding Client-Side Field Level Encryption (CSFLE) for highly sensitive data elements like `password`, `pan_number`, and `aadhar_number`. 

While manual verification and simple scripts have confirmed basic functionality, the app lacks a rigorous, automated integration testing suite. A comprehensive integration test suite will:
1. Guarantee that MongoDB async motor interactions, CSFLE encryption/decryption, and the FastAPI routing layer remain perfectly synchronized.
2. Ensure that core flows (signup, login, document extraction) behave exactly as intended when interacting with the real database rather than relying on brittle mocks.
3. Establish a safe CI/CD boundary to prevent regressions during future refactoring.

## What Changes

We will introduce a full integration testing suite to the `backend/tests/` directory using `pytest`, `pytest-asyncio`, and `httpx`. These tests will hit the actual FastAPI instance coupled with a real (or dedicated CI) MongoDB cluster with CSFLE enabled.

Specifically, the scope of integration tests will cover:
- **Database Lifecycle Management**: Testing init/seed and teardown correctly.
- **CSFLE Identity & Auth Integration**: End-to-end user registration and authentication, verifying that deterministic and random encryptors correctly parse requests into DB fields and decrypt them back to the API layer seamlessly.
- **Extraction Router Integration**: Testing the parallel document extraction pipeline to ensure it handles real structured data uploads, async boundary handling, and validation errors.

## Capabilities

### New Capabilities
- `backend-integration-tests`: A comprehensive API framework integration test suite testing physical data persistence, authentication schemas, and document workflow integrations.

### Modified Capabilities
- 

## Impact

- **Affected code**: New directory `backend/tests/integration/` will be established.
- **Dependencies**: New dev dependencies added to `requirements.txt` (`pytest`, `pytest-asyncio`, `httpx`).
- **Systems**: Testing scripts will be updated to manage MongoDB environment variables correctly.
