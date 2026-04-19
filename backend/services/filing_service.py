from typing import List, Optional
from bson import ObjectId
from backend.db import DatabaseManager
from backend.schemas.filing_schema import FilingAttemptResponse, FilingDocumentSchema
from backend.utils import now_ist
from backend.logger import logger
from backend.constants import ITRType

async def upsert_filing_attempt(user_id: str, assessment_year: str, itr_type: ITRType) -> FilingAttemptResponse:
    """
    Creates or updates a filing attempt. Only one per user per AY.
    """
    db = DatabaseManager.get_db()
    
    query = {
        "user_id": ObjectId(user_id),
        "assessment_year": assessment_year
    }
    
    update = {
        "$set": {
            "itr_type": itr_type,
            "updated_at": now_ist()
        },
        "$setOnInsert": {
            "created_at": now_ist(),
            "documents": []
        }
    }
    
    result = await db.filing_attempts.find_one_and_update(
        query,
        update,
        upsert=True,
        return_document=True
    )
    
    return FilingAttemptResponse.from_mongo(result)

async def get_filing_history(user_id: str) -> List[FilingAttemptResponse]:
    """
    Returns all filing attempts for a user.
    """
    db = DatabaseManager.get_db()
    cursor = db.filing_attempts.find({"user_id": ObjectId(user_id)}).sort("assessment_year", -1)
    results = await cursor.to_list(length=100)
    return [FilingAttemptResponse.from_mongo(r) for r in results]

async def get_filing_by_ay(user_id: str, assessment_year: str) -> Optional[FilingAttemptResponse]:
    db = DatabaseManager.get_db()
    result = await db.filing_attempts.find_one({
        "user_id": ObjectId(user_id),
        "assessment_year": assessment_year
    })
    return FilingAttemptResponse.from_mongo(result) if result else None

async def add_or_update_document(user_id: str, assessment_year: str, doc: FilingDocumentSchema):
    """
    Adds a document to the filing attempt or updates its metadata if it exists (by type).
    Note: We use document type as the unique key within a filing attempt documents array.
    """
    db = DatabaseManager.get_db()
    
    # Check if doc with this type already exists in the array
    existing = await db.filing_attempts.find_one({
        "user_id": ObjectId(user_id),
        "assessment_year": assessment_year,
        "documents.type": doc.type
    })
    
    if existing:
        # Update existing
        await db.filing_attempts.update_one(
            {
                "user_id": ObjectId(user_id),
                "assessment_year": assessment_year,
                "documents.type": doc.type
            },
            {
                "$set": {
                    "documents.$.name": doc.name,
                    "documents.$.is_extraction_complete": doc.is_extraction_complete,
                    "documents.$.total_pages": doc.total_pages,
                    "updated_at": now_ist()
                }
            }
        )
        logger.info(f"Updated document {doc.type} in filing {assessment_year} for user {user_id}")
    else:
        # Push new
        await db.filing_attempts.update_one(
            {
                "user_id": ObjectId(user_id),
                "assessment_year": assessment_year
            },
            {
                "$push": {"documents": doc.model_dump()},
                "$set": {"updated_at": now_ist()}
            }
        )
        logger.info(f"Added new document {doc.type} to filing {assessment_year} for user {user_id}")

async def update_extraction_status(user_id: str, assessment_year: str, doc_type: str, is_complete: bool):
    """Updates only the completion status."""
    db = DatabaseManager.get_db()
    await db.filing_attempts.update_one(
        {
            "user_id": ObjectId(user_id),
            "assessment_year": assessment_year,
            "documents.type": doc_type
        },
        {
            "$set": {
                "documents.$.is_extraction_complete": is_complete,
                "updated_at": now_ist()
            }
        }
    )
