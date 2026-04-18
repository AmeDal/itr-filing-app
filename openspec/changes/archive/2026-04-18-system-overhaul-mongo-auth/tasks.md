## 1. Dependency & SQLite Teardown

- [x] 1.1 Delete `app.db` from the project root.
- [x] 1.2 Update `requirements.txt`: remove `aiosqlite`, add `motor>=3.6.0`.
- [x] 1.3 Remove `*.db` line from `.gitignore`.
- [x] 1.4 Delete dead taxpayer-related artifacts: `backend/controllers/taxpayer_router.py` and `backend/schemas/taxpayer_schema.py`.
- [x] 1.5 Delete dead frontend artifacts: `frontend/src/pages/IdentityVerification.jsx` and `frontend/src/App.css`.

## 2. MongoDB Async Setup & Seeding

- [x] 2.1 Update `backend/settings.py`: Replace `db_path` with `mongo_uri` and `mongo_db_name`.
- [x] 2.2 Rewrite `backend/db.py`: Implement `MongoManager` with `motor`, IST timezone helper, and `generate_oid` hashing function.
- [x] 2.3 Implement Seeding Logic: In `MongoManager.initialize()`, calculate OID for the seed user ("Ameya Pramod Dalvi") and `upsert` it into the `users` collection.
- [x] 2.4 Update `backend/main.py`: Update lifespan to call `MongoManager.initialize()` and `MongoManager.close()`.

## 3. API Refactor (Pure Async Motor)

- [x] 3.1 Rewrite `backend/schemas/user_schema.py`: Update `UserCreateRequest` and `UserResponse` to match the new MongoDB document structure.
- [x] 3.2 Rewrite `backend/services/user_service.py`: Port all logic to use `MongoManager.get_db()` and `motor` collection operations (signup, get_by_oid, get_by_pan, login).
- [x] 3.3 Update `backend/controllers/user_router.py`: Expose only `/signup` and `/login` endpoints.
- [x] 3.4 Refactor `backend/controllers/extraction_router.py`: Replace `DatabaseManager` SQL with `MongoManager` MongoDB operations.
- [x] 3.5 Refactor `backend/services/batch_service.py`: Replace SQL queries with MongoDB `find`, `insert`, and `update` using `motor`.

## 4. UI Radical Redesign

- [x] 4.1 Redesign `frontend/src/index.css`: Implement the new dark-mode premium aesthetic with glassmorphism and micro-animations.
- [x] 4.2 Create `frontend/src/pages/AuthPage.jsx`: Build the unified Login/Signup interface with state-driven rendering and inline validation.
- [x] 4.3 Update `frontend/src/services/api.js`: Refactor to only include `login` and `signup` methods.
- [x] 4.4 Update `frontend/src/App.jsx`: Route root component to `AuthPage`.
- [x] 4.5 Update `frontend/index.html`: Update title and SEO meta tags.
- [x] 4.6 Implement robust client-side validation in `AuthPage.jsx` (PAN, Aadhar, Mobile, Pincode).

## 5. Verification & Finalization

- [x] 5.1 Run `pip install -r requirements.txt` and verify server startup.
- [x] 5.5 Update `AGENTS.md` to reflect the new codebase structure.
