## ADDED Requirements

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

### Requirement: Direct text extraction for LLM
The system SHALL extract all textual content from the PDF and send it as a text part to the LLM for data extraction, rather than converting pages to images.

#### Scenario: Text extraction for PAN/Aadhar
- **WHEN** text is detected in the PDF
- **THEN** the system MUST extract the text and include it in the `contents` list sent to the Gemini API as a `types.Part.from_text` or equivalent string payload

#### Scenario: Text extraction fails or is insufficient
- **WHEN** text extraction returns minimal or garbled content (less than a reasonable threshold, e.g., 50 characters)
- **THEN** the system SHALL fallback to image conversion to ensure extraction accuracy
