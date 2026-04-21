## Context

The codebase currently uses PyMuPDF in two places:

1. `backend/services/llm_service.py` for direct PDF text extraction and OCR fallback for PAN/Aadhar uploads.
2. `backend/services/itr_processing_service.py` for page counting and per-page PNG generation during ITR document processing.

Both flows run inside async functions. Even when the expensive Gemini call is awaited asynchronously, the local PDF work still executes inline on the event loop.

## Goals / Non-Goals

**Goals:**
- Ensure PyMuPDF parsing and rasterization execute off the event-loop thread.
- Reuse one PDF helper across both extraction paths.
- Keep the public API and document-processing behavior unchanged.
- Add focused automated coverage for the offloading boundary.

**Non-Goals:**
- Re-architecting extraction to a process pool or external job system in this change.
- Changing prompt structure, page batching limits, or blob-storage persistence semantics.
- Adding password support to the ITR upload flow, which does not currently expose that input.

## Decisions

1. **Shared helper service**: Add `backend/services/pdf_service.py` with synchronous PyMuPDF routines and async wrappers that call them using `asyncio.to_thread()`.
2. **LLM extraction contract**: The helper returns either extracted text or rendered PNG bytes; `llm_service.py` remains responsible for building Gemini `contents`.
3. **ITR processing contract**: `itr_processing_service.py` uses one helper call to get page count and another to render only the missing pages, minimizing behavior change while removing inline PyMuPDF calls from the coroutine.
4. **Testing strategy**: Add async tests that monkeypatch `asyncio.to_thread()` and service dependencies so we can prove the wrapper boundary is exercised without needing real PDFs.

## Risks / Trade-offs

- **Trade-off**: `asyncio.to_thread()` uses the interpreter thread pool, which is the smallest safe change but not necessarily the highest-throughput option for very large PDFs.
- **Risk**: Rendering selected pages still opens the PDF again after page counting. That is acceptable for the minimum fix and keeps the code easier to reason about.
- **Future option**: If workloads become CPU-saturated, the shared helper is now a clean seam for moving to a dedicated executor or external worker.
