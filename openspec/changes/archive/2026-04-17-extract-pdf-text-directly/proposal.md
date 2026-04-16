## Why

Currently, the system converts every page of a PDF document (like Aadhar or PAN) into an image (PNG) before sending it to the LLM for data extraction. This is inefficient if the PDF already contains embedded, readable text. Extracting text directly from the PDF when available will reduce processing time, lower the payload size to the LLM, and improve overall system performance.

## What Changes

- Update `extract_pan_data` and `extract_aadhar_data` in `backend/services/llm_service.py`.
- Introduce logic to detect if the PDF has textual content using PyMuPDF (`fitz`).
- If sufficient text is present, extract it directly and send the text payload to the Gemini API instead of image blocks.
- Preserve the existing image-conversion fallback for scanned documents (image-only PDFs).

## Capabilities

### New Capabilities
- `pdf-text-extraction`: Direct text extraction from PDF files and evaluation of text content versus image fallback.

### Modified Capabilities

## Impact

- **Code Affected**: `backend/services/llm_service.py`
- **Dependencies**: Relies on existing `PyMuPDF` (`fitz`) library, no new dependencies required.
- **System Impact**: Improved latency and reduced API payload for text-based PDF documents.
