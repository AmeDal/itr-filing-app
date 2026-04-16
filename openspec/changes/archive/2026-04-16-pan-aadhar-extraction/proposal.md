## Why

To allow users to file their ITR smoothly, the system must securely collect and verify core identity information from their PAN and Aadhar cards (Number, Name, DOB, Address). An automated system using LLM-based extraction paired with frontend user validation is essential to gather this data without manual data entry from the user, while simultaneously preventing OCR hallucinations from corrupting the primary database records.

## What Changes

- Introduces document extraction endpoints that use Gemini 3.1 to read PAN and Aadhar card images and return structured JSON.
- Adds stateful API logic to capture the user-verified data and save it.
- Establishes the `taxpayers` SQLite database schema with `pan_number` as the primary key.
- Adds functionality to link subsequent Aadhar uploads to existing PAN profiles.
- Initializes a `documents` table to maintain audit trails for uploaded files.

## Capabilities

### New Capabilities
- `document-extraction`: Logic and endpoints to process PAN/Aadhar images via Gemini and enforce strict JSON schemas for returned data.
- `taxpayer-management`: APIs and DB interactions for creating base Taxpayer profiles and updating them with Aadhar links upon user confirmation.

### Modified Capabilities
- None.

## Impact

- **Backend Architecture**: Requires new FastAPI routers (for extraction and taxpayers), Pydantic schemas, and Service layers communicating with the Gemini SDK.
- **Database**: Introduction of SQLite database with two initial tables (`taxpayers`, `documents`).
- **Dependencies**: Need to include Google GenAI SDK for the Gemini integration.
