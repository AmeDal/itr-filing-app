## MODIFIED Requirements

### Requirement: In-Memory Processing
All document processing (PDF to image conversion and Gemini API payload preparation) MUST occur strictly in RAM. No temporary files or disk-based caching of source documents is allowed.

#### Scenario: Successful PDF Extraction
- **WHEN** a valid PDF is uploaded
- **THEN** it is converted into 200 DPI PNG images in-memory and processed in concurrent batches of 5
- **AND** the PyMuPDF parsing and rasterization work MUST execute off the event-loop thread
