## 1. OpenSpec Context

- [x] 1.1 Create a change for issue `#17` covering PyMuPDF event-loop offloading.
- [x] 1.2 Add spec deltas for async processing and PDF text extraction behavior.

## 2. Backend Refactor

- [x] 2.1 Create `backend/services/pdf_service.py` with thread-offloaded wrappers around PyMuPDF operations.
- [x] 2.2 Update `backend/services/llm_service.py` to use the shared PDF helper instead of calling PyMuPDF inline.
- [x] 2.3 Update `backend/services/itr_processing_service.py` to offload PDF page counting and rasterization before page tasks run.

## 3. Verification

- [x] 3.1 Add automated tests covering the new thread-offloading boundary and service integration.
- [x] 3.2 Run the relevant backend test subset for the new PDF offloading flow.
