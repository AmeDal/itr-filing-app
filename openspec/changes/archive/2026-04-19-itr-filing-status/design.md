## Context

The current `ITRProcessingService` tracks document extraction progress in an in-memory `SessionManager`. While efficient for live updates via SSE, it lacks durability. The system also uses a legacy `documents` collection for a separate single-doc extraction flow which is now redundant.

## Goals / Non-Goals

**Goals:**
- Persist extraction status to MongoDB in a new `filing_attempts` collection.
- Implement a recovery mechanism that avoids redundant Gemini API calls for same-file re-uploads.
- Provide a clear UI for users to manage their filings and re-upload failed docs.
- Standardize document types using a global Enum.
- Remove all legacy `documents` collection code.

**Non-Goals:**
- Automating the storage of uploaded files (we only store extraction metadata and blob-stored JSONs).
- Implementing full OCR for `TRADING_REPORT` in this phase (it will be stored but not processed).
- Refactoring the core Gemini extraction engine itself.

## Decisions

1.  **Collection Name**: `filing_attempts`. Structure:
    ```javascript
    {
      _id: ObjectId,
      user_id: ObjectId,
      assessment_year: String, // "AY-YYYY-YY"
      itr_type: String,        // Enum
      documents: [{
        name: String,
        type: String,          // Enum
        is_extraction_complete: Boolean,
        total_pages: Number
      }],
      created_at: DateTime,
      updated_at: DateTime
    }
    ```
2.  **Recovery Logic**:
    - Calculate MD5 hash of uploaded file in memory.
    - Check blob storage for the `{user_id}/{ay}/{doc_type}/{hash}/` prefix.
    - If hash matches and extraction is partial: Compare `expected_pages` vs `existing_blobs` and only process missing pages.
    - If hash is new: Wipe old blob folder (if different hash for same slot) and start fresh.
3.  **No `file_hash` in MongoDB**: To keep the DB clean and avoid privacy concerns, the hash is only used transiently during upload/recovery.
4.  **Enum usage**: `AS26`, `AIS`, `TIS`, `FORM_16`, `TRADING_REPORT`, `BANK_STATEMENT`, `OTHER`.
5.  **Re-upload**: Users must delete or trigger a "replace" which deliberate hassle to avoid accidental double-charges/processing.

## Risks / Trade-offs

- **Risk**: Blob storage consistency. If a blob write fails but DB updates, the recovery logic might skip a page.
- **Trade-off**: Not storing the uploaded file means we can't "re-extract" without the user providing the file again if we change the prompt logic later.
- **Complexity**: Managing two sources of truth (DB for status, Blobs for data) requires careful transactional logic (DB updated *after* successful blob write).
