import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, HTTPException
from sse_starlette.sse import EventSourceResponse

from backend.services.itr_processing_service import ITRProcessingService, SessionManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/itr", tags=["ITR Processing"])


@router.post("/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...), # TODO: Extract from Auth Token later
    ay: str = Form(...),
    itr_type: str = Form(...),
    doc_types: str = Form(...), # JSON list e.g. ["FORM_26AS", "AIS", ...]
    files: List[UploadFile] = File(...),
):
    """
    Accepts multiple ITR documents and starts in-memory processing.
    """
    import json
    try:
        dt_list = json.loads(doc_types)
    except Exception:
        raise HTTPException(status_code=400, detail="doc_types must be a valid JSON list")

    if len(dt_list) != len(files):
        raise HTTPException(
            status_code=400, 
            detail=f"Mismatch: {len(dt_list)} doc types for {len(files)} files"
        )

    session_id = str(uuid.uuid4())
    
    # Prepare session metadata
    doc_metadata = []
    processed_files = []
    
    for file, doc_type in zip(files, dt_list):
        file_bytes = await file.read()
        file_hash = ITRProcessingService.calculate_file_hash(file_bytes)
        
        doc_metadata.append({
            "file_name": file.filename,
            "file_hash": file_hash,
            "doc_type": doc_type
        })
        
        processed_files.append({
            "name": file.filename,
            "bytes": file_bytes,
            "type": doc_type,
            "hash": file_hash
        })

    SessionManager.create_session(session_id, doc_metadata)
    
    # Start background tasks
    for pf in processed_files:
        background_tasks.add_task(
            ITRProcessingService.process_document,
            session_id, user_id, ay, pf["type"], pf["name"], pf["bytes"]
        )

    return {"session_id": session_id, "message": "Upload successful. Processing started."}


@router.get("/progress/{session_id}")
async def get_progress_stream(session_id: str):
    """
    SSE endpoint to track processing progress.
    """
    return EventSourceResponse(SessionManager.subscribe(session_id))


@router.post("/retry/{session_id}/{file_hash}")
async def retry_extraction(
    session_id: str,
    file_hash: str,
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    ay: str = Form(...),
    doc_type: str = Form(...),
):
    # This is a simplified retry - in a real app, we'd need to re-upload or 
    # keep the bytes in a short-lived cache (like Redis or memory).
    # For now, we assume the user re-uploads or we find a way to re-trigger.
    # TODO: Implement robust byte-level retry logic if needed.
    return {"message": "Retry logic triggered (Stub)"}


@router.post("/force-reparse/{session_id}/{file_hash}")
async def force_reparse(
    session_id: str,
    file_hash: str,
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    ay: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Identical to upload but explicitly sets force_reparse=True.
    """
    file_bytes = await file.read()
    background_tasks.add_task(
        ITRProcessingService.process_document,
        session_id, user_id, ay, doc_type, file.filename, file_bytes, force_reparse=True
    )
    return {"message": "Force re-parse started."}
