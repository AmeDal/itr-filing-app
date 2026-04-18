import logging
from typing import List

from fastapi import APIRouter, HTTPException

from backend.schemas.user_schema import (UserCreateRequest, 
                                        UserLinkAadharRequest, 
                                        UserResponse)
from backend.services import user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_or_update_user(req: UserCreateRequest):
    try:
        return await user_service.create_or_update_user(req)
    except Exception:
        logger.exception("Failed to upsert user")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[UserResponse])
async def list_users():
    return await user_service.list_all_users()


@router.get("/{pan_number}", response_model=UserResponse)
async def get_user(pan_number: str):
    user = await user_service.get_user_by_pan(pan_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{pan_number}", response_model=UserResponse)
async def link_aadhar(pan_number: str, req: UserLinkAadharRequest):
    try:
        return await user_service.link_aadhar(pan_number, req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("Failed to link Aadhar")
        raise HTTPException(status_code=500, detail="Internal server error")
