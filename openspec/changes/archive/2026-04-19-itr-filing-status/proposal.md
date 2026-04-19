## Why

The current ITR processing system only tracks status in-memory, meaning all progress is lost if the backend restarts. Additionally, there is no dashboard for users to see their past filing attempts or resumes interrupted extractions. The legacy `documents` collection also needs to be retired in favor of a more robust `filing_attempts` model.

## What Changes

1.  **Filing Attempts Tracking**: A new MongoDB collection `filing_attempts` will store the state of ITR filing sessions, including document-level extraction status.
2.  **Extraction Resiliency**: The extraction logic will be updated to persist status changes to MongoDB after every page and use a set-difference algorithm to resume interrupted extractions without redundant work.
3.  **Filing History Dashboard**: A new frontend page will allow users to view, manage, and re-upload documents for their filing attempts.
4.  **Legacy Cleanup**: The legacy single-image extraction batch system (`documents` collection, `batch_service.py`, relevant routes) will be completely removed.

## Capabilities

### New Capabilities
- `filing-tracking`: Persistent tracking of ITR filing status across restarts.
- `filing-recovery`: Resuming interrupted extractions using blob storage page sets.
- `filing-dashboard`: User interface for viewing history and managing re-uploads.

### Modified Capabilities
- `itr-processing`: Updated to handle persistence and recovery logic.

## Impact

- **Backend**: New `filing_attempts` collection, updated `ITRProcessingService`, new `filing_router`, removal of `batch_service` and `documents` collection usage.
- **Frontend**: New `FilingHistoryPage`, updated `DocumentUploadPage` to use new constants, and expanded `apiService`.
- **Storage**: Blob storage remains the source of truth for extracted JSONs, but MongoDB will now track which pages are "done".
