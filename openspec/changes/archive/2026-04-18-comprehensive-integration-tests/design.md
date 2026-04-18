## Context

The backend is built asynchronously with FastAPI and Motor (MongoDB async driver). The most sensitive data elements (passwords, PANs, Aadhar numbers) are processed dynamically through CSFLE encryption logic. Given the complexity of the deterministic and random encryption models intertwined with `ObjectId` generation based on plaintext identity fields, purely mocking these layers is inadequate and risky. We need rigorous integration tests to confirm data flows correctly across the entire stack.

## Goals / Non-Goals

**Goals:**
- Test end-to-end integration flows (Signup -> Login -> Extraction).
- Assert correct integration with the MongoDB explicitly using CSFLE encryption/decryption on actual documents.
- Provide a scalable Pytest framework for future API tests.

**Non-Goals:**
- **Unit Testing**: We are not focusing on isolated unit testing of standard utility functions right now.
- **Frontend E2E**: This is strictly targeting the backend API integration layers.
- **Extensive mocking**: We explicitly avoid mocking `CryptoService` or `DatabaseManager` as their real-world behaviors are precisely what we are testing. 

## Decisions

1. **Framework**: We will use `pytest`, `pytest-asyncio`, and `httpx`. `httpx.AsyncClient` lets us send HTTP requests directly to the FastAPI `app` object without starting a live server port, seamlessly interacting with the async event loop.
2. **Database Segregation**: To avoid mutating the developer's main database, the test suite will use an `.env.test` file or a global pytest fixture to securely override `settings.mongo_db_name` to `AmeDal_test`. It will use the exact same cluster but an isolated database.
3. **CSFLE Key Management**: Test environment variables will include a static `CSFLE_MASTER_KEY` generated solely for the `AmeDal_test` DB to ensure tests are environment-agnostic and don't rely on local developer keys.
4. **Fixture Scoping**: We will create an `event_loop` fixture properly scoped. We will use a `db_cleanup` fixture to wipe the `users` and `documents` collections in `AmeDal_test` before each test ensures test idempotency.

## Risks / Trade-offs

- **Risk**: Long-running tests due to network overhead with MongoDB Atlas Free Tier.
  - **Mitigation**: Run setup and teardown effectively using `delete_many({})` rather than destroying/recreating collections, significantly reducing operational lag.
- **Risk**: Test suite accidentally targets the production/dev DB.
  - **Mitigation**: Add a rigorous assertion inside the top-level Pytest fixture: `assert settings.mongo_db_name.endswith("_test")` before invoking `DatabaseManager.initialize()`.
