from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserCreateRequest(BaseModel):
    pan_number: str
    full_name: str
    dob: Optional[date] = None
    father_name: Optional[str] = None


class UserLinkAadharRequest(BaseModel):
    aadhar_number: str
    gender: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    pan_number: str
    full_name: str
    aadhar_number: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[date] = None
    father_name: Optional[str] = None
    gender: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
