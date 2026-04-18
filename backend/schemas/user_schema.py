from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    middle_name: str = ""
    last_name: str = Field(..., min_length=1)
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$")
    aadhar_number: str = Field(..., pattern=r"^[0-9]{12}$")
    aadhar_pincode: str = Field(..., pattern=r"^[0-9]{6}$")
    mobile_number: str = Field(..., pattern=r"^[0-9]{10}$")
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLoginRequest(BaseModel):
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$")
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    id: str = Field(..., alias="_id")
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    pan_number: str
    aadhar_number: Optional[str] = None
    aadhar_pincode: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("id", mode="before")
    @classmethod
    def transform_id(cls, v: Any) -> str:
        return str(v)
