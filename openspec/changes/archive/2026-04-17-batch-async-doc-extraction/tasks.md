## 1. Database Schema & Models

- [x] 1.1 Update `backend/db.py` to add `batch_id` column to the `documents` table.
- [x] 1.2 Update `backend/schemas/extraction_schema.py` to include any new fields for batch responses.

## 2. Backend Orchestration

- [x] 2.1 Implement `backend/services/batch_service.py` to manage background extraction tasks.
- [x] 2.2 Update `backend/services/llm_service.py` if needed to ensure thread-safety or improved error handling during batch runs. (Reviewed: current async/retry logic is sufficient).

## 3. API Endpoints

- [x] 3.1 Create `POST /api/extract/batch` to handle multiple file uploads and initiate background processing.
- [x] 3.2 Create `GET /api/extract/status/{batch_id}` to return the status of all documents in a batch.

## 4. Frontend UI Components

- [x] 4.1 Update `DocumentUpload` component to support multi-file drag-and-drop/selection.
- [x] 4.2 Build a `BatchQueue` component to display selected files and their individual statuses.
- [x] 4.3 Implement polling logic in the frontend to fetch status updates every 2 seconds until all tasks are finished.

## 5. Verification & Testing

- [x] 5.1 Test batch upload with multiple PAN and Aadhar combinations.
- [x] 5.2 Verify that the UI updates correctly from `queued` to `processing` to `completed`.
- [x] 5.3 Test error handling by uploading unsupported or corrupted files.
