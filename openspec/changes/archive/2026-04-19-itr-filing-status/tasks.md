## 1. Constants & Schema Initialization

- [ ] 1.1 Create `backend/constants.py` with `DocumentType` (using `AS26`) and `ITRType` enums.
- [ ] 1.2 Create `frontend/src/constants/docTypes.js` to match backend enums.
- [ ] 1.3 Create `backend/schemas/filing_schema.py` for `filing_attempts` models.
- [ ] 1.4 Update `backend/services/prompt_templates.py` to use `DocumentType.AS26`.

## 2. Database & Service Layer

- [ ] 2.1 Update `backend/db.py`: replace `documents` indexes with `filing_attempts` indexes (compound unique index on `user_id`, `assessment_year`).
- [ ] 2.2 Create `backend/services/filing_service.py` for `filing_attempts` CRUD (one filing per AY, upsert logic).

## 3. Backend Logic & Recovery

- [ ] 3.1 Update `backend/services/blob_service.py`: add `list_existing_pages` and `delete_hash_folder`.
- [ ] 3.2 Update `backend/services/itr_processing_service.py`: implement recovery logic (MD5 hash check, pending pages set-difference).
- [ ] 3.3 Update `backend/services/itr_processing_service.py`: ensure `TRADING_REPORT` is stored in the collection document but NOT processed (no extraction).
- [ ] 3.4 Update `backend/services/itr_processing_service.py`: persist status updates and page completion to MongoDB via `filing_service`.

## 4. API Endpoints

- [ ] 4.1 Create `backend/controllers/filing_router.py` with endpoints for history listing and re-upload.
- [ ] 4.2 Update `backend/controllers/itr_router.py`: use persistent `filing_attempts` and remove hardcoded user TODO.
- [ ] 4.3 Register `filing_router` in `backend/main.py`.

## 5. Frontend Dashboard

- [ ] 5.1 Implement `getFilingHistory`, `getFilingDetail`, and `reuploadDocument` in `frontend/src/services/api.js`.
- [ ] 5.2 Create `frontend/src/pages/FilingHistoryPage.jsx` with card-based history and re-upload UI.
- [ ] 5.3 Update `frontend/src/pages/DocumentUploadPage.jsx` to use new enum constants and the new API flow.
- [ ] 5.4 Update `frontend/src/App.jsx` and `AppLayout.jsx` with routes and navigation for Filing History.

## 6. Cleanup & Migration

- [ ] 6.1 Remove `backend/services/batch_service.py`.
- [ ] 6.2 Completely discard and remove `backend/controllers/extraction_router.py`.
- [ ] 6.3 Update `backend/services/user_deletion_service.py` and `backend/tests/conftest.py` to target `filing_attempts`.
