# Implementation Tasks

## Phase 1: Infrastructure & Shared Logic
- [ ] **Task 1.1**: Install dependencies (`azure-storage-blob`, `sse-starlette`, `react-router-dom`).
- [ ] **Task 1.2**: Update `backend/settings.py` with Azure Blob Storage configuration and credentials.
- [ ] **Task 1.3**: Implement `backend/services/blob_service.py` with async support for Azure Blob (Upload, Check, Overwrite).
- [ ] **Task 1.4**: Implement `backend/services/prompt_templates.py` with detailed extraction prompts for all 7 ITR document types.

## Phase 2: Processing Engine & Router
- [ ] **Task 2.1**: Implement `backend/services/itr_processing_service.py` with in-memory PDF rendering and `asyncio.Semaphore(5)` queue.
- [ ] **Task 2.2**: Integrate rate-limit retry logic and page-level persistence in the processing engine.
- [ ] **Task 2.3**: Implement `backend/controllers/itr_router.py` with `/upload`, `/progress` (SSE), and management endpoints.
- [ ] **Task 2.4**: Register `itr_router` in `backend/main.py`.

## Phase 3: Frontend Foundation & Navigation
- [ ] **Task 3.1**: Initialize `react-router-dom` in `App.jsx` and define all post-login routes.
- [ ] **Task 3.2**: Implement `ITRSelectionPage.jsx` with AY dropdown and selectable ITR type cards.
- [ ] **Task 3.3**: Extend `frontend/src/services/api.js` with new ITR-related endpoints and SSE client.

## Phase 4: Upload Flow & Dashboard
- [ ] **Task 4.1**: Implement `FileDropzone` component with validation and visual feedback.
- [ ] **Task 4.2**: Implement `DocumentUploadPage.jsx` with sequential 7-step upload logic and Form 16 warning modal.
- [ ] **Task 4.3**: Implement `ProgressDashboardPage.jsx` with real-time SSE updates and page-level progress bars.
- [ ] **Task 4.4**: Implement "Results Summary" page for post-processing display.

## Phase 5: Polish & UX
- [ ] **Task 5.1**: Add Premium CSS styles for all new pages using glassmorphism and smooth transitions.
- [ ] **Task 5.2**: Implement airtight exception handling and user-friendly error messages across the flow.
- [ ] **Task 5.3**: Add TODOs for Auth Guard and `user_oid` path normalization as per feedback.
- [ ] **Task 5.4**: Add the Architecture Overview diagram to the repository for future agents (as requested).
