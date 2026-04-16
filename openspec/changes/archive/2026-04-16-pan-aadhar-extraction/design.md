## Context

The ITR filing app needs to reliably collect and store the taxpayer's identity information (PAN as primary, Aadhar as linked entity) from uploaded documents. Since OCR and LLM extraction are non-deterministic, we are implementing a flow that abstracts LLM execution behind a stateless extraction API and requires the client to confirm data before committing changes to an SQLite database.

## Goals / Non-Goals

**Goals:**
- Provide a robust way to extract data from PAN and Aadhar images using Gemini 3.1.
- Ensure the database is only populated with user-verified information, effectively treating the LLM as an assistant rather than a direct database updater.
- Standardize the FastAPI backend architecture following `routers -> service -> db` patterns.

**Non-Goals:**
- Frontend React implementation (This change focuses exclusively on backend APIs for extraction and database modeling).
- Filing tax returns or communicating directly with income tax portals at this stage.

## Decisions

**1. "Verify then Save" Architecture**
Instead of a single endpoint that uploads a file, extracts data, and automatically saves it, we decouple this into two endpoints:
1. `POST /api/v1/extract/...`: Stateless. Uploads image to Gemini, returns structured JSON.
2. `POST /api/v1/taxpayers/`: Stateful. Receives confirmed JSON from the frontend and commits to the `taxpayers` SQLite table.
*Rationale:* Protects data integrity. If Gemini misreads a date (e.g. 1990 vs 1998), the user fixes it on the frontend before `POST`ing the verified data to the backend.

**2. SQLite as the Primary Data Store**
We will use Python's built-in `sqlite3` or a lightweight ORM like `SQLModel`/`databases` (staying within the boundaries of the `db.py` layer of the `.gemini/GEMINI.md` rules).
*Rationale:* Keeps the app self-contained and avoids heavy database infrastructure for a single-user or small-scale local app.

**3. Gemini 3.1 for Data Extraction**
We will utilize the `google-genai` SDK with Structured Outputs (JSON Schema) to enforce the response format from the vision model.
*Rationale:* Ensures the Python backend always receives a parsable Pydantic schema rather than unpredictable raw text.

## Risks / Trade-offs

- **Risk: Gemini Hallucinations** -> *Mitigation*: The "Verify then Save" architecture is specifically designed to mitigate this. The user is the final arbiter of truth.
- **Risk: Aadhar uploaded before PAN** -> *Mitigation*: The Linking logic requires a PAN to exist. The API will enforce that an Aadhar payload sent to `PATCH /api/v1/taxpayers/{pan_number}` fails gracefully (404 Not Found) if the `pan_number` doesn't exist yet.
