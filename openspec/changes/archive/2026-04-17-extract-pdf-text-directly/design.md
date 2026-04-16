## Context

The current document extraction logic in `backend/services/llm_service.py` handles PDF files by converting each page into a 200 DPI PNG image. This image-based approach is necessary for scanned documents but inefficient for "born-digital" PDFs that already contain selectable text. Sending raw text to the Gemini API is faster, uses fewer tokens, and often yields more accurate results for character-heavy documents like PAN or Aadhar PDFs.

## Goals / Non-Goals

**Goals:**
- Identify if a PDF contains extractable text using PyMuPDF.
- Implement a threshold-based fallback: if text content is minimal (suggesting a scanned image embedded in a PDF), the system will revert to the image-conversion workflow.
- Send a single text block to the LLM instead of multiple images when text is available.
- Refactor `llm_service.py` to share this logic between PAN and Aadhar extraction.

**Non-Goals:**
- Supporting encrypted or password-protected PDFs beyond current `fitz` capabilities.
- Implementing complex layout or table extraction from PDFs; the LLM handles raw text well enough for the required schemas.

## Decisions

### 1. Unified PDF Processor Helper
**Decision:** Create a helper function `get_pdf_content(image_bytes: bytes) -> tuple[bool, list[types.Part]]`.
**Rationale:** `extract_pan_data` and `extract_aadhar_data` both handle PDFs identically. A unified helper ensures consistency and reduces code duplication.

### 2. Text vs. Image Heuristic
**Decision:** Use a character count threshold (e.g., 50 characters) to determine "readability."
**Rationale:** Many scanned PDFs contain a few metadata characters but no actual document text. A threshold ensures we don't accidentally send "empty" text payloads when an image-based approach would be superior.
**Alternatives Considered:** Checking for the presence of fonts. However, font detection is more complex and less reliable than simply checking if text extraction yields actual characters.

### 3. payload Structure
**Decision:** When text is extracted, it will be added as a single `types.Part.from_text` or a string in the `contents` list.
**Rationale:** Gemini 2.0/Pro models handle long text inputs efficiently. Combining all pages into one text block simplifies the prompt context.

## Risks / Trade-offs

- **[Risk] Scanned OCR Layer** → Some scanned documents have a low-quality hidden OCR layer. Direct extraction might get garbled text while the image is clear.
- **[Mitigation]** The heuristic can be tuned. If extraction results are consistently poor, we can raise the character threshold or allow users to "force OCR" in the future.
- **[Risk] Formatting Loss** → `get_text()` might lose some visual layout cues (like label-value proximity) compared to an image.
- **[Mitigation]** The prompt already instructs the LLM to "analyze the provided document(s) accurately." Modern LLMs are highly robust to raw text layout variations.
