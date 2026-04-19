import json
from typing import Any, Dict, List, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient

from backend.logger import logger
from backend.settings import get_settings


class BlobStorageService:
    """
    Service for interacting with Azure Blob Storage asynchronously.
    """
    _client: Optional[BlobServiceClient] = None

    @classmethod
    def get_client(cls) -> BlobServiceClient:
        """Returns the shared BlobServiceClient instance."""
        if not cls._client:
            settings = get_settings()
            if not settings.azure_storage_connection_string:
                logger.error("AZURE_STORAGE_CONNECTION_STRING is not set.")
                raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing.")

            cls._client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string)
        return cls._client

    @classmethod
    async def ensure_container(cls):
        """Ensures the configured container exists."""
        settings = get_settings()
        client = cls.get_client()
        container_client = client.get_container_client(
            settings.azure_storage_container_name)
        try:
            await container_client.get_container_properties()
        except ResourceNotFoundError:
            logger.info(
                f"Container '{settings.azure_storage_container_name}' not found. Creating..."
            )
            await container_client.create_container()
            logger.info(
                f"Container '{settings.azure_storage_container_name}' created."
            )

    @classmethod
    async def save_page_json(cls, user_id: str, ay: str, doc_type: str,
                             file_hash: str, page_index: int, data: Dict[str,
                                                                         Any]):
        """
        Saves extraction result for a single page to Azure Blob Storage.
        Path: {user_id}/{ay}/{doc_type}/{file_hash}/page_{page_index}.json
        """
        settings = get_settings()
        # ay is expected to be in format "AY-YYYY-YY"
        blob_name = f"{user_id}/{ay}/{doc_type}/{file_hash}/page_{page_index}.json"

        client = cls.get_client()
        # Ensure container exists before first upload
        await cls.ensure_container()

        container_client = client.get_container_client(
            settings.azure_storage_container_name)
        blob_client = container_client.get_blob_client(blob_name)

        content = json.dumps(data, indent=2)
        await blob_client.upload_blob(content, overwrite=True)
        logger.info(f"Saved blob: {blob_name}")

    @classmethod
    async def check_extraction_complete(cls, user_id: str, ay: str,
                                        doc_type: str, file_hash: str,
                                        expected_pages: int) -> bool:
        """
        Checks if all pages for a document have already been extracted.
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/{file_hash}/"

        client = cls.get_client()
        try:
            container_client = client.get_container_client(
                settings.azure_storage_container_name)

            count = 0
            async for blob in container_client.list_blobs(
                    name_starts_with=prefix):
                if blob.name.endswith(".json"):
                    count += 1

            is_complete = count == expected_pages
            if is_complete:
                logger.info(
                    f"Found complete extraction in cache for {file_hash} ({count} pages)"
                )
            return is_complete
        except ResourceNotFoundError:
            # Container doesn't exist, so extraction definitely not complete
            return False
        except Exception as e:
            logger.error(f"Error checking blob cache: {e}")
            return False

    @classmethod
    async def get_all_page_results(cls, user_id: str, ay: str, doc_type: str,
                                   file_hash: str) -> List[Dict[str, Any]]:
        """
        Retrieves all page JSONs for a specific document.
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/{file_hash}/page_"

        client = cls.get_client()
        results = []

        container_client = client.get_container_client(
            settings.azure_storage_container_name)

        # List blobs and fetch content
        blobs = []
        try:
            async for blob in container_client.list_blobs(
                    name_starts_with=prefix):
                blobs.append(blob.name)
        except ResourceNotFoundError:
            return []

        # Sort by name to ensure page order (page_0, page_1...)
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
    async def delete_user_blobs(cls, user_id: str):
        """
        Deletes all blobs under the user's root prefix.
        """
        settings = get_settings()
        prefix = f"{user_id}/"
        client = cls.get_client()

        try:
            container_client = client.get_container_client(
                settings.azure_storage_container_name)
            async for blob in container_client.list_blobs(
                    name_starts_with=prefix):
                logger.info(f"Deleting blob: {blob.name}")
                await container_client.delete_blob(blob.name)
        except ResourceNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error deleting user blobs: {e}")
            raise e

    @classmethod
    async def get_existing_hash_for_slot(cls, user_id: str, ay: str, doc_type: str) -> Optional[str]:
        """
        Returns the file hash used in the existing blob path for this document slot, if any.
        Path structure: {user_id}/{ay}/{doc_type}/{hash}/...
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/"
        client = cls.get_client()
        
        try:
            container_client = client.get_container_client(settings.azure_storage_container_name)
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                # path is user_id/ay/doc_type/HASH/page_N.json
                parts = blob.name.split("/")
                if len(parts) >= 4:
                    return parts[3]
            return None
        except Exception as e:
            logger.error(f"Error getting existing hash for slot: {e}")
            return None

    @classmethod
    async def delete_doc_blobs(cls, user_id: str, ay: str, doc_type: str):
        """
        Deletes all blobs for a specific document slot (all hashes).
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/"
        client = cls.get_client()
        
        try:
            container_client = client.get_container_client(settings.azure_storage_container_name)
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                logger.info(f"Deleting blob for slot recovery: {blob.name}")
                await container_client.delete_blob(blob.name)
        except ResourceNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error deleting doc blobs: {e}")

    @classmethod
    async def list_existing_pages(cls, user_id: str, ay: str, doc_type: str, file_hash: str) -> List[int]:
        """
        Returns a list of page indices that are already extracted for this hash.
        """
        settings = get_settings()
        prefix = f"{user_id}/{ay}/{doc_type}/{file_hash}/page_"
        client = cls.get_client()
        indices = []
        
        try:
            container_client = client.get_container_client(settings.azure_storage_container_name)
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                try:
                    idx = int(blob.name.split("page_")[-1].split(".json")[0])
                    indices.append(idx)
                except Exception:
                    continue
            return indices
        except ResourceNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error listing existing pages: {e}")
            return []

    @classmethod
    async def close(cls):
        """Closes the client and its transport."""
        if cls._client:
            await cls._client.close()
            cls._client = None
