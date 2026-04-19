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
    password: str = Field(..., min_length=12)

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        from backend.security import validate_password_strength
        is_valid, err = validate_password_strength(v)
        if not is_valid:
            raise ValueError(err)
        return v


class UserLoginRequest(BaseModel):
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$")
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(..., alias="_id")
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    pan_number: str
    aadhar_number: Optional[str] = None
    aadhar_pincode: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("id", mode="before")
    @classmethod
    def transform_id(cls, v: Any) -> str:
        return str(v)

    @field_validator("pan_number",
                     "aadhar_number",
                     "mobile_number",
                     mode="after")
    @classmethod
    def mask_pii(cls, v: Optional[str]) -> Optional[str]:
        if not v or len(str(v)) < 4:
            return v
        s = str(v)
        return "*" * (len(s) - 4) + s[-4:]

    @field_validator("email", mode="after")
    @classmethod
    def mask_email(cls, v: Optional[str]) -> Optional[str]:
        if not v or "@" not in str(v):
            return v
        s = str(v)
        parts = s.split("@")
        name = parts[0]
        if len(name) <= 1:
            return "*" + "@" + parts[1]
        return name[0] + "*" * (len(name) - 1) + "@" + parts[1]


class UserSummary(BaseModel):
    """Minimal user info for UI context without sensitive PII."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    # id: str = Field(..., alias="_id")  # Removed for security (Metadata leakage)
    first_name: str
    last_name: str
    role: str
    is_active: bool

    # @field_validator("id", mode="before")
    # @classmethod
    # def transform_id(cls, v: Any) -> str:
    #     return str(v)


class AuthResponse(BaseModel):
    """Login response with tokens + user summary."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserSummary


class TokenRefreshResponse(BaseModel):
    """Response from /users/refresh — no body-level refresh token (cookie only)."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
