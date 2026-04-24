## Why

Issue #17 identified a responsiveness risk in the PDF pipeline: PyMuPDF work is currently executed inside async request and background-processing coroutines. Calls such as `fitz.open()`, `page.get_text()`, `page.get_pixmap()`, and `pix.tobytes()` can monopolize the event-loop thread and delay unrelated API traffic, SSE progress updates, and auth operations.

## What Changes

1. Introduce a shared PDF service that runs PyMuPDF operations in worker threads via `asyncio.to_thread()`.
2. Refactor direct PDF extraction (`llm_service.py`) to use the threaded helper for text detection and PDF rasterization fallback.
3. Refactor batch ITR processing (`itr_processing_service.py`) so page counting and PNG rendering are offloaded before Gemini page tasks are scheduled.
4. Add regression tests that verify the threaded wrappers are used by the async services.

## Capabilities

### Modified Capabilities
- `async-processing-engine`: PDF parsing and rasterization must not execute on the event-loop thread.
- `pdf-text-extraction`: Direct-text detection and OCR fallback must use the same offloaded PDF pipeline.

## Impact

- **Backend**: New shared PDF helper service, updated extraction services, and test coverage for thread offloading.
- **Runtime**: Event-loop responsiveness improves during PDF-heavy requests while preserving the current API shape.
- **Future Work**: This keeps the minimum fix small while leaving room for a later `ProcessPoolExecutor` or external worker if PDF workloads grow.
