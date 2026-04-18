import json
import logging
from typing import Any, Dict, List, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient

from backend.settings import get_settings

logger = logging.getLogger(__name__)


class BlobStorageService:
    """
    Service for interacting with Azure Blob Storage asynchronously.
    """
    _client: Optional[BlobServiceClient] = None

    @classmethod
    def get_client(cls) -> BlobServiceClient:
        if not cls._client:
            settings = get_settings()
            cls._client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
        return cls._client

    @classmethod
    async def save_page_json(
        cls,
        user_id: str,
        ay: str,
        doc_type: str,
        file_hash: str,
        page_index: int,
        data: Dict[str, Any]
    ):
        """
        Saves extraction result for a single page to Azure Blob Storage.
        Path: {user_id}/{ay}/{doc_type}/{file_hash}/page_{page_index}.json
        """
        settings = get_settings()
        blob_name = f"{user_id}/{ay}/{doc_type}/{file_hash}/page_{page_index}.json"
        
        client = cls.get_client()
        async with client:
            container_client = client.get_container_client(settings.azure_storage_container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            content = json.dumps(data, indent=2)
            await blob_client.upload_blob(content, overwrite=True)
            logger.info(f"Saved blob: {blob_name}")

    @classmethod
    async def check_extraction_complete(
        cls,
        user_id: str,
        ay: str,
        doc_type: str,
        file_hash: str,
        expected_pages: int
    ) -> bool:
        """
        Checks if all pages for a document have already been extracted.
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/{file_hash}/"
        
        client = cls.get_client()
        async with client:
            container_client = client.get_container_client(settings.azure_storage_container_name)
            
            count = 0
            try:
                async for blob in container_client.list_blobs(name_starts_with=prefix):
                    if blob.name.endswith(".json"):
                        count += 1
                
                is_complete = count == expected_pages
                if is_complete:
                    logger.info(f"Found complete extraction in cache for {file_hash} ({count} pages)")
                return is_complete
            except Exception as e:
                logger.error(f"Error checking blob cache: {e}")
                return False

    @classmethod
    async def get_all_page_results(
        cls,
        user_id: str,
        ay: str,
        doc_type: str,
        file_hash: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all page JSONs for a specific document.
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/{file_hash}/page_"
        
        client = cls.get_client()
        results = []
        async with client:
            container_client = client.get_container_client(settings.azure_storage_container_name)
            
            # List blobs and fetch content
            blobs = []
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                blobs.append(blob.name)
            
            # Sort by name to ensure page order (page_0, page_1...)
            # Note: page_10 would come before page_2 if simple sort, 
            # so we sort by index if possible.
            def get_index(name: str):
                try:
                    return int(name.split("page_")[-1].split(".json")[0])
                except Exception:
                    return 0
            
            blobs.sort(key=get_index)
            
            for blob_name in blobs:
                blob_client = container_client.get_blob_client(blob_name)
                stream = await blob_client.download_blob()
                content = await stream.readall()
                results.append(json.loads(content))
                
        return results

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
