## Context

Currently, the application supports document extraction but lacks a coordinated batch processing workflow. Users must wait for one document to finish before starting another, or manually manage multiple uploads. This design addresses the need for a multi-document extraction system with asynchronous background processing and real-time status tracking.

## Goals / Non-Goals

**Goals:**
- Support multiple file selection in the frontend.
- Allow users to review a "queue" of selected files before starting extraction.
- Process documents in the background without blocking the UI.
- Provide clear visual feedback on the progress of each file (Pending -> Extracting -> Success/Error).
- Persist extraction results and statuses in the database.

**Non-Goals:**
- Support for hundreds of documents at once (limited to typical tax filing docs: 2-5).
- Complex job scheduling (using simple FastAPI `BackgroundTasks`).
- WebSocket communication (polling will be used for simplicity unless requirements change).

## Decisions

- **Session Identification**: Use a UUID-based `batch_id` to group multiple document extraction tasks.
- **Background Processing**: Use FastAPI's `BackgroundTasks` to trigger `llm_service` calls. This avoids the overhead of a dedicated task queue like Celery while the app is small.
- **Progress Tracking**: 
    - Frontend will poll a new `GET /api/extract/status/{batch_id}` endpoint every 2-3 seconds.
    - Backend will update the `documents` table's `status` column as processing progresses.
- **Database Schema Updates**: 
    - Add `batch_id` column to the `documents` table.
    - Statuses: `queued`, `extracting`, `completed`, `error`.

## Risks / Trade-offs

- **Rate Limiting**: Concurrent calls to Gemini API might hit rate limits. The current `llm_service` has retry logic, but a high number of concurrent files could still cause delays. *Mitigation*: Process batch files sequentially or with limited concurrency in the backend worker logic.
- **Polling Overhead**: Frequent polling can add load to the server. *Mitigation*: Polling only active while the extraction session is running, and the number of concurrent documents is low.
