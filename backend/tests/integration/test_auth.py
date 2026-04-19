import pytest
from httpx import AsyncClient
from backend.db import DatabaseManager
from backend.services.crypto_service import CryptoService
from backend.utils import mask_pii, mask_email


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
        "email": "johndoe@example.com",
        "password": "SuperSecretPassword123!"
    }

    # 1. API interaction
    response = await async_client.post("/api/v1/users/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    # Validate masking using the official utility function
    assert data["pan_number"] == mask_pii(payload["pan_number"])

    # 2. Raw MongoDB assertions
    db = DatabaseManager.get_db()
    # PAN is stored encrypted, so searching by plaintext should fail
    plaintext_query = await db.users.find_one({"pan_number": "ABCDE1234F"})
    assert plaintext_query is None, "PAN was not encrypted in DB!"


@pytest.mark.asyncio
async def test_auth_lifecycle_integration(async_client: AsyncClient):
    """
    End-to-end lifecycle: Signup -> Login -> Access Me -> Refresh -> Logout -> Access Denied
    """
    email = "lifecycle@example.com"
    pan = "LIFEC1234E"
    password = "LifecyclePassword123!"

    # 1. Signup
    signup_resp = await async_client.post("/api/v1/users/signup",
                                          json={
                                              "first_name": "Life",
                                              "last_name": "Cycle",
                                              "pan_number": pan,
                                              "aadhar_number": "123412341234",
                                              "aadhar_pincode": "123456",
                                              "mobile_number": "9000000000",
                                              "email": email,
                                              "password": password
                                          })
    assert signup_resp.status_code == 201

    # 2. Login & Get Access Token + Refresh Cookie
    login_resp = await async_client.post("/api/v1/users/login",
                                         data={
                                             "username": pan,
                                             "password": password
                                         })
    assert login_resp.status_code == 200
    data = login_resp.json()
    token = data["access_token"]

    # 3. Access Protected /me
    me_resp = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()

    # Validate masking using official utilities
    assert me_data["email"] == mask_email(email)
    assert me_data["pan_number"] == mask_pii(pan)

    # 4. Refresh Token (Rotate)
    refresh_resp = await async_client.post("/api/v1/users/refresh",
                                           cookies=login_resp.cookies)
    assert refresh_resp.status_code == 200
    new_token = refresh_resp.json()["access_token"]

    # 5. Access with New Token
    me_resp_2 = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me_resp_2.status_code == 200

    # 6. Logout (Revoke tokens)
    logout_resp = await async_client.post(
        "/api/v1/users/logout",
        headers={"Authorization": f"Bearer {new_token}"},
        cookies=refresh_resp.cookies)
    assert logout_resp.status_code == 200

    # 7. Verify Revocation (401)
    me_resp_revoked = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me_resp_revoked.status_code == 401


@pytest.mark.asyncio
async def test_admin_access_control(async_client: AsyncClient):
    """
    Verifies that RBAC strictly blocks standard users from admin endpoints.
    """
    # 1. Create standard user
    pan = "USERX1234Y"
    password = "UserPassword123!"
    await async_client.post("/api/v1/users/signup",
                            json={
                                "first_name": "Standard",
                                "last_name": "User",
                                "pan_number": pan,
                                "aadhar_number": "999988887777",
                                "aadhar_pincode": "400001",
                                "mobile_number": "8888777766",
                                "email": "user@example.com",
                                "password": password
                            })

    login_resp = await async_client.post("/api/v1/users/login",
                                         data={
                                             "username": pan,
                                             "password": password
                                         })
    assert login_resp.status_code == 200
    user_token = login_resp.json()["access_token"]

    # 2. Attempt admin access (expect 403)
    admin_resp = await async_client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {user_token}"})
    assert admin_resp.status_code == 403
    assert "Admin privileges required" in admin_resp.json()["detail"]
