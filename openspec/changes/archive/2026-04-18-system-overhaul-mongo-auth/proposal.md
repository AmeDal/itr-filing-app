## Why

The current system relies on a locally stored SQLite database (`app.db`) using `aiosqlite`, which is unsuitable for scaling or multi-user environments. Furthermore, the codebase contains significant "dead code" (taxpayer routers/schemas) and a complex, multi-step document extraction UI that creates excessive friction for new users.

This change migrates the backend to a production-grade async MongoDB architecture (using `motor`) and radically simplifies the user experience by replacing the complex onboarding flow with a minimalist, premium Login/Signup interface. This shift establishes a robust foundation for future ITR filing capabilities while immediately improving system performance and reliability.

## What Changes

1. **Database Migration**: Complete removal of SQLite (`aiosqlite`) and implementation of an async MongoDB driver (`motor`). Teardown of existing `.sqlite` files.
2. **Architecture Update**: Implementation of a clean `MongoManager` in `db.py`, IST-timezone-aware date handling, and a deterministic OID generation function for users.
3. **API Refactor**: Complete rewrite of user-related APIs to a pure async approach. Removal of dead endpoints and old taxpayer-specific logic. 
4. **UI Radical Redesign**: Replacement of the complex `IdentityVerification.jsx` flow with a high-polish, minimalist `AuthPage.jsx` supporting Login and Signup.
5. **Data Seeding**: Automated seeding of an initial administrative user ("Ameya Pramod Dalvi") with precise OID computation.

## Capabilities

### New Capabilities
- `user-auth`: Full authentication lifecycle including secure Signup (OID-based) and Login (PAN + Mobile).
- `mongo-persistence`: Asynchronous persistence layer using MongoDB for users and document records.

### Modified Capabilities
- `document-extraction`: The extraction process will be updated to store metadata and status in MongoDB instead of SQLite. Requirements for how extraction records are linked to users remain the same, but the underlying persistence model changes.

## Impact

- **Backend**: `main.py` (lifespan), `db.py` (complete rewrite), `user_service.py` (complete rewrite), `user_router.py` (simplified), `extraction_router.py` (SQL -> MongoDB), `batch_service.py` (SQL -> MongoDB).
- **Frontend**: `App.jsx` (routing), `api.js` (refactored methods), `index.css` (global aesthetic redesign), `index.html` (SEO).
- **Dependencies**: Remove `aiosqlite`, add `motor`.
- **Infrastructure**: New MongoDB connection string requirement in environment.
