import json
import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sse_starlette.sse import EventSourceResponse

from backend.auth_deps import UserPrincipal, get_current_user
from backend.logger import logger
from backend.services.itr_processing_service import ITRProcessingService, SessionManager
from backend.services import filing_service
from backend.constants import ITRType

router = APIRouter(prefix="/v1/itr", tags=["ITR Processing"])


def validate_ay(ay: str):
    """Validates assessment year format AY-YYYY-YY."""
    import re
    if not re.match(r"^AY-\d{4}-\d{2}$", ay):
        raise HTTPException(
            status_code=400,
            detail="Invalid Assessment Year format. Expected AY-YYYY-YY (e.g. AY-2025-26)"
        )


@router.post("/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    ay: str = Form(...),
    itr_type: str = Form(...),
    doc_types: str = Form(...), # JSON list e.g. ["AS26", "AIS", ...]
    files: List[UploadFile] = File(...),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Accepts multiple ITR documents and starts persistent processing.
    """
    validate_ay(ay)
    logger.info(f"ITR upload initiated for user {current_user.id} - {ay} - {itr_type}")
    
    try:
        dt_list = json.loads(doc_types)
    except Exception:
        raise HTTPException(status_code=400, detail="doc_types must be a valid JSON list")

    if len(dt_list) != len(files):
        raise HTTPException(
            status_code=400, 
            detail=f"Mismatch: {len(dt_list)} doc types for {len(files)} files"
        )

    # 1. Initialize Filing Attempt in DB
    try:
        await filing_service.upsert_filing_attempt(current_user.id, ay, ITRType(itr_type))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Check for completed documents to block accidental re-upload
    existing_filing = await filing_service.get_filing_by_ay(current_user.id, ay)
    if existing_filing:
        completed_types = {d.type for d in existing_filing.documents if d.is_extraction_complete}
        intersect = set(dt_list).intersection(completed_types)
        if intersect:
            raise HTTPException(
                status_code=400, 
                detail=f"Documents already completed: {', '.join(intersect)}. Please delete them first to re-upload."
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
            "type": doc_type # Renamed from doc_type to type for consistency
        })
        
        processed_files.append({
            "name": file.filename,
            "bytes": file_bytes,
            "type": doc_type,
            "hash": file_hash
        })

    SessionManager.create_session(session_id, current_user.id, doc_metadata)
    # Ensure AY is stored for recovery persistence task
    SessionManager._sessions[session_id]["assessment_year"] = ay
    
    # Start background tasks
    for pf in processed_files:
        background_tasks.add_task(
            ITRProcessingService.process_document,
            session_id, current_user.id, ay, pf["type"], pf["name"], pf["bytes"]
        )

    return {"session_id": session_id, "message": "Upload successful. Processing started."}


@router.get("/progress/{session_id}")
async def get_progress_stream(
    session_id: str,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    SSE endpoint to track processing progress.
    Scoped to the authenticated session owner.
    """
    return EventSourceResponse(SessionManager.subscribe(session_id, current_user.id))
