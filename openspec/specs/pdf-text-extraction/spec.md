## Capability: PDF Text Extraction

### Requirement: Detect Textual Content in PDF
The PDF helper service SHALL use PyMuPDF (`fitz`) to detect embedded textual content before deciding whether to return direct text or rendered page images.

#### Scenario: PDF contains readable text
- **WHEN** a PDF file with extractable text is processed by `extract_pdf_payload`
- **THEN** the service detects text and returns it for direct LLM use
- **AND** PyMuPDF parsing and text extraction execute off the event-loop thread.

#### Scenario: PDF is scanned or image-only
- **WHEN** a PDF file has no sufficient extractable text
- **THEN** the service falls back to in-memory page rasterization
- **AND** page rasterization executes off the event-loop thread.

### Requirement: Direct Text Extraction for LLM Helpers
The direct PAN/Aadhar extraction helpers SHALL send extracted text to Gemini when sufficient text is available.

#### Scenario: Text extraction for PAN/Aadhar helper
- **WHEN** text is detected in the PDF
- **THEN** the helper includes that text in the Gemini contents payload.

#### Scenario: Text extraction fails or is insufficient
- **WHEN** text extraction returns minimal or garbled content below the configured threshold
- **THEN** the helper falls back to image conversion.
