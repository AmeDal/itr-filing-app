from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TaxpayerCreateRequest(BaseModel):
    pan_number: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: str
    dob: Optional[date] = None
    father_name: Optional[str] = None


class TaxpayerLinkAadharRequest(BaseModel):
    aadhar_number: str
    gender: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = None


class TaxpayerResponse(BaseModel):
    pan_number: str
    aadhar_number: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: str
    dob: Optional[date] = None
    father_name: Optional[str] = None
    gender: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = None
    created_at: datetime

