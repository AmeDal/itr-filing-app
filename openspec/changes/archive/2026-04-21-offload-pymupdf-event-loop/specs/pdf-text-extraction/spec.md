## MODIFIED Requirements

### Requirement: Detect textual content in PDF
The system SHALL use PyMuPDF (`fitz`) to detect if a PDF document contains embedded textual content before deciding whether to perform OCR (image conversion).

#### Scenario: PDF contains readable text
- **WHEN** a PDF file with extractable text is uploaded
- **THEN** the system MUST detect the presence of text and proceed with direct text extraction
- **AND** the PyMuPDF parsing and text extraction work MUST execute off the event-loop thread

#### Scenario: PDF is scanned or image-only
- **WHEN** a PDF file with no extractable text is uploaded
- **THEN** the system MUST fallback to the existing image-conversion (OCR) workflow
- **AND** the page rasterization work MUST execute off the event-loop thread
