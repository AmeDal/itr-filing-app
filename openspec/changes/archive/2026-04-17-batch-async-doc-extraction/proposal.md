## Why

Current document extraction is likely handled synchronously or individually, which can lead to a poor user experience when multiple documents need processing. Users should be able to upload all required documents (PAN, Aadhar) at once and track their extraction progress asynchronously to avoid blocking the UI and provide clear feedback on long-running tasks.

## What Changes

- **Frontend**:
    - Update the document upload interface to support multiple file selection.
    - Implement a "Queue" view showing selected files before processing starts.
    - Add a "Process All" button to initiate batch extraction.
    - Introduce a real-time progress indicator (e.g., status badges, progress bars) for each file in the batch.
- **Backend**:
    - Add a new endpoint to handle batch document upload and queuing.
    - Implement asynchronous task handling (likely using FastAPI's `BackgroundTasks` or a simple internal queue for now) to process documents in the background.
    - Create a status endpoint or WebSocket handler to provide progress updates (Pending -> Processing -> Completed/Error).
    - Ensure database schema supports tracking extraction status and linking multiple documents to a single extraction session/user.

## Capabilities

### New Capabilities
- `batch-doc-processing`: Orchestrates the asynchronous extraction of multiple documents in a single session.
- `extraction-status-api`: Provides real-time or polled updates on the state of background extraction tasks.

### Modified Capabilities
- `document-extraction`: Likely needs modification to support higher concurrency or to be wrapped by the batch orchestrator.

## Impact

- `backend/services/llm_service.py`: Will be leveraged for the actual extraction logic, but might need optimization for concurrent calls (rate limiting is already partially handled).
- `frontend/src/pages/DocumentUpload.jsx` (hypothetical): Major UI overhaul to support the batch workflow.
- `backend/main.py`: New routers for batch status.
- `backend/db.py`: Updates to track job/task status.
