import asyncio
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List

from google.genai import types

from backend.logger import logger
from backend.services.blob_service import BlobStorageService
from backend.services.llm_service import _generate_content_with_retry, get_client
from backend.services.pdf_service import get_pdf_page_count, render_pdf_pages
from backend.services.prompt_templates import get_prompt_for_doc_type
from backend.services import filing_service
from backend.schemas.filing_schema import FilingDocumentSchema
from backend.constants import DocumentType
from backend.settings import get_settings


class SessionManager:
    """
    Manages in-memory state of processing sessions and broadcasts progress.
    """
    _sessions: Dict[str, Dict[str, Any]] = {}
    _listeners: Dict[str, List[asyncio.Queue]] = {}

    @classmethod
    def create_session(cls, session_id: str, owner_user_id: str,
                       documents: List[Dict[str, Any]]):
        cls._sessions[session_id] = {
            "status": "processing",
            "owner_user_id": owner_user_id,
            "documents": {
                doc["file_hash"]: {
                    **doc, "completed_pages": 0,
                    "status": "queued"
                }
                for doc in documents
            },
            "created_at": datetime.now().isoformat()
        }
        cls._listeners[session_id] = []

    @classmethod
    def update_progress(cls,
                        session_id: str,
                        file_hash: str,
                        page_index: int,
                        total_pages: int,
                        status: str = "processing"):
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

                # Persist to DB if completed
                if doc["status"] == "completed" or (total_pages > 0 and doc["completed_pages"] == total_pages):
                    asyncio.create_task(filing_service.update_extraction_status(
                        cls._sessions[session_id]["owner_user_id"],
                        cls._sessions[session_id].get("assessment_year", ""),
                        doc.get("type", ""),
                        True
                    ))

                cls.broadcast(session_id)

    @classmethod
    def broadcast(cls, session_id: str):
        if session_id in cls._sessions and session_id in cls._listeners:
            state = cls._sessions[session_id]
            for queue in cls._listeners[session_id]:
                queue.put_nowait(json.dumps(state))

    @classmethod
    async def subscribe(cls, session_id: str, user_id: str):
        if session_id in cls._sessions and cls._sessions[session_id][
                "owner_user_id"] != user_id:
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
    async def process_document(cls,
                               session_id: str,
                               user_id: str,
                               ay: str,
                               doc_type: str,
                               file_name: str,
                               file_bytes: bytes,
                               force_reparse: bool = False):
        file_hash = cls.calculate_file_hash(file_bytes)
        
        # Ensure assessment_year is in SessionManager for DB updates
        if session_id in SessionManager._sessions:
            SessionManager._sessions[session_id]["assessment_year"] = ay

        # 0. Handle TRADING_REPORT (Metadata only, no extraction)
        if doc_type == DocumentType.TRADING_REPORT:
            logger.info(f"Skipping extraction for {doc_type} - marked as complete (metadata only).")
            await filing_service.add_or_update_document(
                user_id, ay, 
                FilingDocumentSchema(name=file_name, type=doc_type, is_extraction_complete=True, total_pages=0)
            )
            SessionManager.update_progress(session_id, file_hash, 0, 0, status="completed")
            return

        # 1. Recovery Check: Hash comparison
        existing_hash = await BlobStorageService.get_existing_hash_for_slot(user_id, ay, doc_type)
        if existing_hash and existing_hash != file_hash:
            logger.info(f"File hash changed for {doc_type} ({existing_hash} -> {file_hash}). Wiping old blobs.")
            await BlobStorageService.delete_doc_blobs(user_id, ay, doc_type)
            # We don't return here, we progress as a fresh upload

        # 2. Convert PDF to images in-memory
        try:
            total_pages = await get_pdf_page_count(file_bytes)
        except Exception as e:
            logger.error(f"Failed to open PDF {file_name}: {e}")
            SessionManager.update_progress(session_id, file_hash, 0, 1, status="error")
            return

        # 3. Update DB with initial document state
        await filing_service.add_or_update_document(
            user_id, ay, 
            FilingDocumentSchema(name=file_name, type=doc_type, is_extraction_complete=False, total_pages=total_pages)
        )

        # 4. Filter missing pages (Recovery)
        existing_pages = await BlobStorageService.list_existing_pages(user_id, ay, doc_type, file_hash)
        pages_to_process = [i for i in range(total_pages) if i not in existing_pages]
        
        # Update session with existing progress
        doc_info = SessionManager._sessions.get(session_id, {}).get("documents", {}).get(file_hash)
        if doc_info:
            doc_info["completed_pages"] = len(existing_pages)
            doc_info["type"] = doc_type # Ensure type is available for DB update task

        if not pages_to_process:
            logger.info(f"All {total_pages} pages for {doc_type} already extracted. Skipping.")
            SessionManager.update_progress(session_id, file_hash, total_pages, total_pages, status="completed")
            return

        SessionManager.update_progress(session_id, file_hash, len(existing_pages), total_pages, status="extracting")

        # 5. Process remaining pages
        rendered_pages = await render_pdf_pages(file_bytes, pages_to_process, dpi=200)
        tasks = []
        for i, img_bytes in rendered_pages:
            tasks.append(
                cls._process_single_page(session_id, user_id, ay, doc_type,
                                         file_hash, i, total_pages, img_bytes))

        await asyncio.gather(*tasks)

    @classmethod
    async def _process_single_page(cls, session_id: str, user_id: str, ay: str,
                                   doc_type: str, file_hash: str,
                                   page_index: int, total_pages: int,
                                   img_bytes: bytes):
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
                        response_mime_type="application/json", ),
                )

                result_data = json.loads(response.text)

                # Save to Blob Storage
                await BlobStorageService.save_page_json(
                    user_id, ay, doc_type, file_hash, page_index, result_data)

                SessionManager.update_progress(session_id,
                                               file_hash,
                                               page_index,
                                               total_pages,
                                               status="completed_page")

            except Exception as e:
                logger.error(
                    f"Error processing page {page_index} of {file_hash}: {e}")
                SessionManager.update_progress(session_id,
                                               file_hash,
                                               page_index,
                                               total_pages,
                                               status="failed_page")

    @classmethod
    async def process_session(cls, session_id: str, user_id: str, ay: str, processed_files: List[Dict[str, Any]]):
        """
        Orchestrates processing for all documents in a session concurrently.
        """
        logger.info(f"Starting concurrent processing orchestrator for session {session_id}")
        tasks = []
        for pf in processed_files:
            tasks.append(
                cls.process_document(
                    session_id, user_id, ay, pf["type"], pf["name"], pf["bytes"]
                )
            )
        
        # Run all documents in parallel. return_exceptions=True ensures that one failure
        # doesn't prevent other documents from being processed.
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Concurrent processing orchestrator finished for session {session_id}")
