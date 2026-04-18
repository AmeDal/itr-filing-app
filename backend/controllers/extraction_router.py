import logging
import uuid
import json
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Form, BackgroundTasks

from backend.db import DatabaseManager
from backend.services.llm_service import extract_pan_data, extract_aadhar_data
from backend.services.batch_service import initialize_batch, process_batch_extraction
from backend.schemas.extraction_schema import (BatchExtractionInitiatedResponse, 
                                               BatchStatusResponse, 
                                               DocumentStatusResponse)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/extract", tags=["Extraction"])


@router.post("/document")
async def extract_document(
    doc_type: str = Form(..., description="Either 'PAN' or 'AADHAR'"),
    file: UploadFile = File(...),
    password: Optional[str] = Form(None)
):
    if doc_type.upper() not in ["PAN", "AADHAR"]:
        raise HTTPException(status_code=400, detail="doc_type must be PAN or AADHAR")

    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"

    try:
        if doc_type.upper() == "PAN":
            data = await extract_pan_data(image_bytes, mime_type, password)
            return {"status": "success", "data": data}
        else:
            data = await extract_aadhar_data(image_bytes, mime_type, password)
            return {"status": "success", "data": data}
    except Exception:
        logger.exception("Document extraction failed")
        raise HTTPException(status_code=500, detail="Extraction failed")


@router.post("/batch", response_model=BatchExtractionInitiatedResponse)
async def extract_batch_docs(
    background_tasks: BackgroundTasks,
    doc_types: str = Form(..., description="JSON list of doc types"),
    files: List[UploadFile] = File(...),
    passwords: Optional[str] = Form(None, description="JSON list of passwords")
):
    # Parse doc_types
    try:
        dt_list = json.loads(doc_types)
        if not isinstance(dt_list, list):
            dt_list = [str(dt_list)]
    except Exception:
        dt_list = [d.strip() for d in doc_types.split(",")]

    if len(dt_list) != len(files):
        logger.error(f"Mismatch: {len(dt_list)} types vs {len(files)} files")
        raise HTTPException(status_code=400, detail=f"Number of doc_types ({len(dt_list)}) must match number of files ({len(files)})")
    
    # Parse passwords
    p_list = [None] * len(files)
    if passwords:
        try:
            p_parsed = json.loads(passwords)
            if isinstance(p_parsed, list):
                p_list = p_parsed
            else:
                p_list = [str(p_parsed)]
        except Exception:
            p_list = [p.strip() if p.strip() else None for p in passwords.split(",")]

    # Final normalization
    if len(p_list) < len(files):
        p_list.extend([None] * (len(files) - len(p_list)))

    batch_id = str(uuid.uuid4())
    
    # Initialize batch in DB and read files
    prepared_files = await initialize_batch(batch_id, files, [dt.upper() for dt in dt_list], p_list)
    
    # Queue background task
    background_tasks.add_task(process_batch_extraction, batch_id, prepared_files)
    
    return BatchExtractionInitiatedResponse(batch_id=batch_id)


@router.get("/status/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str):
    async with DatabaseManager.get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM documents WHERE batch_id = ? ORDER BY created_at ASC",
            (batch_id,)
        )
        rows = await cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        documents = []
        all_done = True
        for row in rows:
            status = row["status"]
            if status in ["queued", "extracting"]:
                all_done = False
                
            documents.append(DocumentStatusResponse(
                id=row["id"],
                batch_id=row["batch_id"],
                doc_type=row["doc_type"],
                status=status,
                error_message=row["error_message"],
                extraction_data=json.loads(row["extracted_data"]) if row["extracted_data"] else None,
                created_at=row["created_at"]
            ))
            
        return BatchStatusResponse(
            batch_id=batch_id,
            documents=documents,
            is_completed=all_done
        )
