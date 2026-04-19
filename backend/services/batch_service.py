import asyncio
import logging
import uuid
from typing import List, Optional

from fastapi import UploadFile

from backend.db import DatabaseManager
from backend.services import user_service
from backend.services.llm_service import extract_aadhar_data, extract_pan_data
from backend.utils import map_error_to_friendly_message, now_ist

logger = logging.getLogger(__name__)


async def process_single_document(
    doc_id: str,
    file_bytes: bytes,
    mime_type: str,
    password: Optional[str] = None
):
    """
    Handles extraction for a single document record and links it to a user.
    """
    db = DatabaseManager.get_db()
    try:
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {"status": "extracting"}}
        )

        row = await db.documents.find_one({"id": doc_id})
        doc_type = row["doc_type"] if row else "unknown"

        result = None
        if doc_type == "PAN":
            result = await extract_pan_data(file_bytes, mime_type, password)
        elif doc_type == "AADHAR":
            result = await extract_aadhar_data(file_bytes, mime_type, password)
        else:
            await db.documents.update_one(
                {"id": doc_id},
                {"$set": {"status": "error", "error_message": "Unknown document type"}}
            )
            return

        if result.is_error:
            await db.documents.update_one(
                {"id": doc_id},
                {"$set": {"status": "error", "error_message": result.error_message}}
            )
        else:
            user_oid = None
            if doc_type == "PAN":
                ext = result.extraction_data
                try:
                    user = await user_service.get_user_by_pan(ext.pan_number)
                    if user:
                        user_oid = user.id
                except Exception:
                    logger.warning(f"Could not link doc {doc_id} to user automatically")

            await db.documents.update_one(
                {"id": doc_id},
                {"$set": {
                    "status": "completed",
                    "extracted_data": result.extraction_data.model_dump(),
                    "user_oid": user_oid
                }}
            )

    except Exception as e:
        logger.exception(f"Error processing document {doc_id}")
        friendly_msg = map_error_to_friendly_message(e)
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": {"status": "error", "error_message": friendly_msg}}
        )


async def process_batch_extraction(
    batch_id: str,
    files: List[tuple[str, bytes, str, str, Optional[str]]]
):
    """
    Background task to process a batch of documents in parallel.
    """
    logger.info(f"Starting parallel batch extraction for {batch_id}")

    tasks = [
        process_single_document(doc_id, file_bytes, mime_type, password)
        for doc_id, file_bytes, mime_type, _, password in files
    ]

    await asyncio.gather(*tasks)
    logger.info(f"Completed batch extraction for {batch_id}")


async def initialize_batch(
    batch_id: str,
    files: List[UploadFile],
    doc_types: List[str],
    passwords: List[Optional[str]],
    created_by_user_id: str
) -> List[tuple[str, bytes, str, str, Optional[str]]]:
    """
    Saves initial records to DB and prepares file data for background task.
    """
    prepared_files = []
    db = DatabaseManager.get_db()

    for file, doc_type, password in zip(files, doc_types, passwords):
        doc_id = str(uuid.uuid4())
        file_bytes = await file.read()
        mime_type = file.content_type

        doc_doc = {
            "id": doc_id,
            "batch_id": batch_id,
            "doc_type": doc_type,
            "status": "queued",
            "created_by_user_id": created_by_user_id,
            "created_at": now_ist()
        }
        await db.documents.insert_one(doc_doc)
        prepared_files.append((doc_id, file_bytes, mime_type, file.filename, password))

    return prepared_files
