from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.auth_deps import UserPrincipal, get_current_user
from backend.services import filing_service
from backend.services.blob_service import BlobStorageService
from backend.schemas.filing_schema import FilingAttemptResponse
from backend.logger import logger

router = APIRouter(prefix="/v1/filing", tags=["Filing History"])

@router.get("/history", response_model=List[FilingAttemptResponse])
async def get_history(current_user: UserPrincipal = Depends(get_current_user)):
    """Returns the user's ITR filing history."""
    return await filing_service.get_filing_history(current_user.id)

@router.get("/history/{assessment_year}", response_model=FilingAttemptResponse)
async def get_filing_detail(
    assessment_year: str,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Returns details for a specific assessment year's filing."""
    filing = await filing_service.get_filing_by_ay(current_user.id, assessment_year)
    if not filing:
        raise HTTPException(status_code=404, detail="Filing not found for this assessment year")
    return filing

@router.delete("/history/{assessment_year}/{doc_type}")
async def delete_document_slot(
    assessment_year: str,
    doc_type: str,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Deletes a document from a filing attempt and wipes its associated blobs.
    Required before re-uploading a different file for a completed slot.
    """
    from backend.db import DatabaseManager
    db = DatabaseManager.get_db()
    
    # 1. Remove from MongoDB
    result = await db.filing_attempts.update_one(
        {"user_id": current_user.id_as_obj, "assessment_year": assessment_year},
        {"$pull": {"documents": {"type": doc_type}}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found in this filing")
    
    # 2. Wipe Blobs
    await BlobStorageService.delete_doc_blobs(current_user.id, assessment_year, doc_type)
    
    logger.info(f"User {current_user.id} deleted document {doc_type} for {assessment_year}")
    return {"message": f"Document {doc_type} deleted successfully"}
