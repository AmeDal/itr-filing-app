import pytest
from httpx import AsyncClient
from backend.db import DatabaseManager
from backend.services.crypto_service import CryptoService

@pytest.mark.asyncio
async def test_signup_integration(async_client: AsyncClient):
    """
    Tests end-to-end functionality of signup interacting with the DB securely.
    """
    payload = {
        "first_name": "John",
        "middle_name": "Paul",
        "last_name": "Doe",
        "pan_number": "ABCDE1234F",
        "aadhar_number": "123456789012",
        "aadhar_pincode": "123456",
        "mobile_number": "9876543210",
        "email": "johndoe@example.com", # .example and .com are safer than .test for some validators
        "password": "SuperSecretPassword123!"
    }
    
    # 1. API interaction
    response = await async_client.post("/api/v1/users/signup", json=payload)
    if response.status_code != 201:
        import json
        print(f"FAILED SIGNUP: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201
    
    data = response.json()
    assert data["pan_number"] == "ABCDE1234F"
    
    # 2. Raw MongoDB assertions
    db = DatabaseManager.get_db()
    plaintext_query = await db.users.find_one({"pan_number": "ABCDE1234F"})
    assert plaintext_query is None, "PAN was not encrypted!"
    
    enc_pan = await CryptoService.encrypt_deterministic("ABCDE1234F")
    raw_doc = await db.users.find_one({"pan_number": enc_pan})
    assert raw_doc is not None
    
    import bson
    assert isinstance(raw_doc["pan_number"], bson.binary.Binary)
    assert isinstance(raw_doc["password"], bson.binary.Binary)

@pytest.mark.asyncio
async def test_login_integration(async_client: AsyncClient):
    """
    Validates user credentials against encrypted states.
    """
    pan = "VWXYZ1234G"
    password = "LoginSecret123!"
    
    # 1. Signup
    payload = {
        "first_name": "Login",
        "middle_name": "",
        "last_name": "Tester",
        "pan_number": pan,
        "aadhar_number": "111122223333",
        "aadhar_pincode": "654321",
        "mobile_number": "9998887776",
        "email": "logintester@example.com",
        "password": password
    }
    signup_resp = await async_client.post("/api/v1/users/signup", json=payload)
    assert signup_resp.status_code == 201
    
    # 2. Valid Login test
    login_payload = {
        "pan_number": pan,
        "password": password
    }
    
    response = await async_client.post("/api/v1/users/login", json=login_payload)
    assert response.status_code == 200
    
    # 3. Invalid Login test
    resp_invalid = await async_client.post("/api/v1/users/login", json={
        "pan_number": pan,
        "password": "WrongPassword!"
    })
    assert resp_invalid.status_code == 401
