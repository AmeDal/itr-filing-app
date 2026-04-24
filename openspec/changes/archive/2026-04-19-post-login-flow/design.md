## Context

The system currently handles single document extractions but lacks a batch-oriented, multi-step flow required for complex ITR filings. The goal is to build a "fire-and-forget" upload system that provides real-time progress feedback while ensuring no sensitive documents touch the server's disk.

## Goals / Non-Goals

**Goals:**
- Zero-disk-persistence for uploaded documents.
- Real-time page-by-page progress status.
- Content-based caching of extraction results to avoid redundant API costs.
- Guided, foolproof UI for document collection.
- Resilient processing with automatic retries for rate limits.

**Non-Goals:**
- PDF OCR/text-extraction optimization (relying on Gemini's visual capabilities via images).
- Detailed Form 16 parsing logic (placeholder for this phase).
- Full user session/JWT implementation (using state-based User ID stopgap).

## Decisions

- **In-Memory Rendering**: Use `fitz` (PyMuPDF) to render PDF pages into images at 200 DPI directly into `bytes` objects.
- **Concurrency Control**: A shared `asyncio.Semaphore(5)` will limit concurrent Gemini requests per processing session to prevent early rate-limiting and ensure system stability.
- **Azure Blob Pattern**: Paths: `{user_id}/{AY}/{doc_type}/{file_hash}/page_{i}.json`. Overwrite existing blobs on "Force Re-parse".
- **SSE for Progress**: Implement a `SessionManager` that uses `asyncio.Queue` or simple event listeners to broadcast progress updates to the `/api/v1/itr/progress/{session_id}` SSE stream.
- **UI Sequence**: Documents must be uploaded in a specific order (1-7) to ensure logical consistency for the user.
- **Form 16 UX**: A warning modal will trigger if Form 16 is omitted, explaining the impact on processing.

## Risks / Trade-offs

- **Memory Pressure**: Processing many large PDFs concurrently could spike memory usage. Offset by batching and semaphore limits.
- **SSE Reliability**: Connections might drop. The UI will include reconnect logic and a "fetch latest state" fallback.
- **Auth Security**: Passing `user_id` in state is a temporary risk; mitigated by future JWT integration (TODO added).
