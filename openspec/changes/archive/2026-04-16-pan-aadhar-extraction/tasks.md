## 1. Project Initialization

- [x] 1.1 Scaffold FastAPI backend directory structure (`backend/main.py`, `backend/routers/`, `backend/services/`, `backend/schemas/`)
- [x] 1.2 Add `google-genai`, `fastapi`, `uvicorn`, and `pydantic` to project dependencies
- [x] 1.3 Initialize `backend/db.py` with SQLite connection and `taxpayers`, `documents` table definitions

## 2. Schemas and Services

- [x] 2.1 Create Pydantic schemas in `backend/schemas/extraction_schema.py` for structured LLM outputs (PAN and Aadhar)
- [x] 2.2 Create Pydantic schemas in `backend/schemas/taxpayer_schema.py` for API payloads (Create and Link)
- [x] 2.3 Implement `backend/services/llm_service.py` to wrap `google-genai` SDK and perform structured extraction from image bytes

## 3. API Endpoints

- [x] 3.1 Create `backend/routers/extraction_router.py` with `POST /api/v1/extract/document` returning JSON without saving to DB
- [x] 3.2 Create `backend/routers/taxpayer_router.py` with `POST /api/v1/taxpayers/` to securely save verified PAN records
- [x] 3.3 Add `PATCH /api/v1/taxpayers/{pan_number}` to `taxpayer_router.py` to link verified Aadhar details to an existing PAN profile
- [x] 3.4 Wire up routers and middleware in `backend/main.py`
