## Why

The current ITR filing application lacks a post-login user journey and a scalable document processing engine. Users need a clear, guided flow to select their assessment year and ITR type, upload necessary tax documents, and track parsing progress in real-time without the risk of data loss or privacy breaches (in-memory processing).

## What Changes

- **Frontend Flow**: Implementation of a 3-stage post-login journey: AY & ITR Selection → Sequential Document Upload → Live Processing Dashboard.
- **Processing Engine**: A robust, in-memory async engine using Python `asyncio` and `PyMuPDF` to convert documents to images and extract data via Gemini API.
- **Storage**: Integration with Azure Blob Storage for persisting structured extraction results (JSON) with content-based deduplication (MD5).
- **Real-time UX**: Server-Sent Events (SSE) for live feedback on extraction progress.

## Capabilities

### New Capabilities
- `itr-selection`: Step-by-step selection of Assessment Year and ITR Type with modern UI cards.
- `sequential-document-upload`: Validated upload flow for 7 specific tax document types (Form 26AS, AIS, TIS, Bank Statements, Zerodha P&L, Form 16, Others).
- `async-processing-engine`: In-memory batched (concurrency=5) extraction engine with rate-limit-aware retries.
- `blob-result-caching`: Persistence layer on Azure Blob Storage to skip re-processing of identical documents.
- `live-progress-dashboard`: Real-time tracking of page-by-page extraction status via SSE.

### Modified Capabilities
- `extraction`: Extending existing extraction logic to support multiple document types and batching.

## Impact

- **Backend**: New `itr_router`, `itr_processing_service`, and `blob_service`.
- **Frontend**: New pages and components for selection, upload, and dashboard; integration of `react-router-dom`.
- **Infrastructure**: Azure Blob Storage dependency.
- **API**: Addition of SSE endpoints for real-time status.
