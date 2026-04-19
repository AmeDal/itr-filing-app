import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import fitz
from google.genai import types
from google.genai.errors import APIError

from backend.services.blob_service import BlobStorageService
from backend.services.llm_service import _generate_content_with_retry, get_client
from backend.services.prompt_templates import get_prompt_for_doc_type
from backend.settings import get_settings

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages in-memory state of processing sessions and broadcasts progress.
    """
    _sessions: Dict[str, Dict[str, Any]] = {}
    _listeners: Dict[str, List[asyncio.Queue]] = {}

    @classmethod
    def create_session(cls, session_id: str, owner_user_id: str, documents: List[Dict[str, Any]]):
        cls._sessions[session_id] = {
            "status": "processing",
            "owner_user_id": owner_user_id,
            "documents": {doc["file_hash"]: {**doc, "completed_pages": 0, "status": "queued"} for doc in documents},
            "created_at": datetime.now().isoformat()
        }
        cls._listeners[session_id] = []

    @classmethod
    def update_progress(cls, session_id: str, file_hash: str, page_index: int, total_pages: int, status: str = "processing"):
        if session_id in cls._sessions:
            doc = cls._sessions[session_id]["documents"].get(file_hash)
            if doc:
                doc["total_pages"] = total_pages
                if status == "completed_page":
                    doc["completed_pages"] += 1
                elif status == "completed":
                    doc["completed_pages"] = total_pages
                    doc["status"] = "completed"
                elif status == "failed_page":
                    doc["status"] = "failed"
                else:
                    doc["status"] = status
                
                if doc["completed_pages"] == total_pages:
                    doc["status"] = "completed"
                
                cls.broadcast(session_id)

    @classmethod
    def broadcast(cls, session_id: str):
        if session_id in cls._sessions and session_id in cls._listeners:
            state = cls._sessions[session_id]
            for queue in cls._listeners[session_id]:
                queue.put_nowait(json.dumps(state))

    @classmethod
    async def subscribe(cls, session_id: str, user_id: str):
        if session_id in cls._sessions and cls._sessions[session_id]["owner_user_id"] != user_id:
             # Basic ownership check
             return

        queue = asyncio.Queue()
        if session_id not in cls._listeners:
            cls._listeners[session_id] = []
        cls._listeners[session_id].append(queue)
        
        # Send initial state
        if session_id in cls._sessions:
            queue.put_nowait(json.dumps(cls._sessions[session_id]))
            
        try:
            while True:
                msg = await queue.get()
                yield {"data": msg}
        finally:
            if session_id in cls._listeners:
                cls._listeners[session_id].remove(queue)


class ITRProcessingService:
    """
    In-memory async processing engine for ITR documents.
    """
    _semaphore = asyncio.Semaphore(5)

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        return hashlib.md5(file_bytes).hexdigest()

    @classmethod
    async def process_document(
        cls,
        session_id: str,
        user_id: str, # TODO: Replace with proper Auth session user_oid later
        ay: str,
        doc_type: str,
        file_name: str,
        file_bytes: bytes,
        force_reparse: bool = False
    ):
        file_hash = cls.calculate_file_hash(file_bytes)
        
        # 1. Convert PDF to images in-memory
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
        except Exception as e:
            logger.error(f"Failed to open PDF {file_name}: {e}")
            SessionManager.update_progress(session_id, file_hash, 0, 1, status="error")
            return

        # 2. Check Cache (Blob Storage)
        if not force_reparse:
            is_complete = await BlobStorageService.check_extraction_complete(
                user_id, ay, doc_type, file_hash, total_pages
            )
            if is_complete:
                SessionManager.update_progress(session_id, file_hash, total_pages, total_pages, status="completed")
                return

        SessionManager.update_progress(session_id, file_hash, 0, total_pages, status="extracting")

        # 3. Process Pages in Batches
        tasks = []
        for i in range(total_pages):
            page = doc[i]
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            tasks.append(cls._process_single_page(
                session_id, user_id, ay, doc_type, file_hash, i, total_pages, img_bytes
            ))
        
        await asyncio.gather(*tasks)
        doc.close()

    @classmethod
    async def _process_single_page(
        cls,
        session_id: str,
        user_id: str,
        ay: str,
        doc_type: str,
        file_hash: str,
        page_index: int,
        total_pages: int,
        img_bytes: bytes
    ):
        async with cls._semaphore:
            client = get_client()
            settings = get_settings()
            prompt = get_prompt_for_doc_type(doc_type)

            contents = [
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                prompt
            ]

            try:
                response = await _generate_content_with_retry(
                    client=client,
                    model=settings.gemini_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                result_data = json.loads(response.text)
                
                # Save to Blob Storage
                await BlobStorageService.save_page_json(
                    user_id, ay, doc_type, file_hash, page_index, result_data
                )
                
                SessionManager.update_progress(session_id, file_hash, page_index, total_pages, status="completed_page")
                
            except Exception as e:
                logger.error(f"Error processing page {page_index} of {file_hash}: {e}")
                SessionManager.update_progress(session_id, file_hash, page_index, total_pages, status="failed_page")
