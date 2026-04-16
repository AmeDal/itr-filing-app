import asyncio
import json
import logging
import uuid
from typing import List, Optional

from fastapi import UploadFile

from backend.db import get_db_connection
from backend.schemas.extraction_schema import (AadharExtractionResponse,
                                               PanExtractionResponse)
from backend.services.llm_service import extract_aadhar_data, extract_pan_data
from backend.utils import map_error_to_friendly_message

logger = logging.getLogger(__name__)


async def process_single_document(doc_id: str, file_bytes: bytes, mime_type: str, password: Optional[str] = None):
    """
    Handles extraction for a single document record.
    """
    async with get_db_connection() as db:
        try:
            # Update status to extracting
            await db.execute(
                "UPDATE documents SET status = ? WHERE id = ?",
                ("extracting", doc_id),
            )
            await db.commit()

            # Fetch doc_type
            cursor = await db.execute("SELECT doc_type FROM documents WHERE id = ?", (doc_id,))
            row = await cursor.fetchone()
            doc_type = row["doc_type"] if row else "unknown"

            result = None
            if doc_type == "PAN":
                result = await extract_pan_data(file_bytes, mime_type, password)
            elif doc_type == "AADHAR":
                result = await extract_aadhar_data(file_bytes, mime_type, password)
            else:
                await db.execute(
                    "UPDATE documents SET status = ?, error_message = ? WHERE id = ?",
                    ("error", "Unknown document type", doc_id),
                )
                await db.commit()
                return

            if result.is_error:
                await db.execute(
                    "UPDATE documents SET status = ?, error_message = ? WHERE id = ?",
                    ("error", result.error_message, doc_id),
                )
            else:
                await db.execute(
                    "UPDATE documents SET status = ?, extracted_data = ? WHERE id = ?",
                    ("completed", result.extraction_data.model_dump_json(), doc_id),
                )
            await db.commit()

        except Exception as e:
            logger.exception(f"Error processing document {doc_id}")
            friendly_msg = map_error_to_friendly_message(e)
            await db.execute(
                "UPDATE documents SET status = ?, error_message = ? WHERE id = ?",
                ("error", friendly_msg, doc_id),
            )
            await db.commit()


async def process_batch_extraction(batch_id: str, files: List[tuple[str, bytes, str, str, Optional[str]]]):
    """
    Background task to process a batch of documents in parallel.
    files: List of (doc_id, file_bytes, mime_type, file_name, password)
    """
    logger.info(f"Starting parallel batch extraction for {batch_id}")
    
    # Create tasks for all documents in the batch
    tasks = [
        process_single_document(doc_id, file_bytes, mime_type, password)
        for doc_id, file_bytes, mime_type, _, password in files
    ]
    
    # Run all extractions concurrently
    await asyncio.gather(*tasks)
    
    logger.info(f"Completed batch extraction for {batch_id}")


async def initialize_batch(batch_id: str, files: List[UploadFile], doc_types: List[str], passwords: List[Optional[str]]) -> List[tuple[str, bytes, str, str, Optional[str]]]:
    """
    Saves initial records to DB and prepares file data for background task.
    """
    prepared_files = []
    async with get_db_connection() as db:
        for file, doc_type, password in zip(files, doc_types, passwords):
            doc_id = str(uuid.uuid4())
            file_bytes = await file.read()
            mime_type = file.content_type
            
            # Save to DB as queued
            await db.execute(
                "INSERT INTO documents (id, batch_id, doc_type, status) VALUES (?, ?, ?, ?)",
                (doc_id, batch_id, doc_type, "queued"),
            )
            prepared_files.append((doc_id, file_bytes, mime_type, file.filename, password))
        
        await db.commit()
    
    return prepared_files
