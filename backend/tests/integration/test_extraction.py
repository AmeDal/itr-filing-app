import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_malformed_document_extraction(async_client: AsyncClient):
    """
    Tests the batch upload endpoint with malformed data (requires auth).
    """
    # 1. Setup Auth 
    # Use a valid PAN (5 letters, 4 numbers, 1 letter)
    pan = "EXTRA1234T"
    password = "ExtractPassword123!"
    await async_client.post("/api/v1/users/signup", json={
        "first_name": "Extract", "last_name": "Test", "pan_number": pan,
        "aadhar_number": "111122223333", "aadhar_pincode": "111111",
        "mobile_number": "9999999999", "email": "extract@example.com", "password": password
    })
    login_resp = await async_client.post("/api/v1/users/login", data={"username": pan, "password": password})
    token = login_resp.json()["access_token"]
    
    # 2. Provide an obviously bad physical payload structure 
    bad_pdf_content = b"This is totally not a PDF string data"
    
    # Payload for /api/v1/extract/batch requires doc_types as a form field
    data = {"doc_types": '["PAN"]'}
    files = {"files": ("bad_document.pdf", bad_pdf_content, "application/pdf")}
    
    response = await async_client.post(
        "/api/v1/extract/batch", 
        data=data, 
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # It should return 200 and initiate a batch (errors happen in background task)
    assert response.status_code == 200
    res_json = response.json()
    assert "batch_id" in res_json
