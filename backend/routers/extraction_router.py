import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, Form

from backend.services.llm_service import extract_pan_data, extract_aadhar_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/extract", tags=["Extraction"])


@router.post("/document")
async def extract_document(
    doc_type: str = Form(..., description="Either 'PAN' or 'AADHAR'"),
    file: UploadFile = File(...)
):
    if doc_type.upper() not in ["PAN", "AADHAR"]:
        raise HTTPException(status_code=400, detail="doc_type must be PAN or AADHAR")

    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"

    try:
        if doc_type.upper() == "PAN":
            data = await extract_pan_data(image_bytes, mime_type)
            return {"status": "success", "data": data}
        else:
            data = await extract_aadhar_data(image_bytes, mime_type)
            return {"status": "success", "data": data}
    except Exception:
        logger.exception("Document extraction failed")
        raise HTTPException(status_code=500, detail="Extraction failed")

