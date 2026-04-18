import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_malformed_document_extraction(async_client: AsyncClient):
    """
    Tests the batch upload endpoint with malformed data.
    """
    
    # 1. Provide an obviously bad physical payload structure 
    bad_pdf_content = b"This is totally not a PDF string data"
    
    # Payload for /api/v1/extract/batch requires doc_types as a form field
    data = {"doc_types": '["PAN"]'}
    files = {"files": ("bad_document.pdf", bad_pdf_content, "application/pdf")}
    
    response = await async_client.post("/api/v1/extract/batch", data=data, files=files)
    
    # It should return 200 and initiate a batch (errors happen in background task)
    assert response.status_code == 200
    res_json = response.json()
    assert "batch_id" in res_json
