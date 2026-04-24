from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class PanExtractionSchema(BaseModel):
    pan_number: str = Field(description="The 10-character alphanumeric PAN number")
    first_name: Optional[str] = Field(None, description="First name of the card holder")
    middle_name: Optional[str] = Field(None, description="Middle name of the card holder")
    last_name: str = Field(
        description="Last name or surname. If full name is combined, parse it and put the last word here."
    )
    father_name: Optional[str] = Field(None, description="Father's full name")
    dob: Optional[date] = Field(None, description="Date of birth in YYYY-MM-DD format")


class AadharExtractionSchema(BaseModel):
    aadhar_number: str = Field(description="The 12-digit Aadhar number, without spaces")
    first_name: Optional[str] = Field(None)
    middle_name: Optional[str] = Field(None)
    last_name: str = Field(description="Last name or surname of the card holder")
    dob: Optional[date] = Field(None)
    gender: Optional[str] = Field(None, description="Gender: MALE, FEMALE, or OTHER")
    address_line: Optional[str] = Field(None, description="Full residential address")
    pincode: Optional[str] = Field(None, description="6-digit postal code")


class PanExtractionResponse(BaseModel):
    is_error: bool = Field(description="True if the provided image is NOT a valid PAN card.")
    error_message: Optional[str] = Field(
        None, description="If is_error is true, describe why (e.g. 'Image too blurry', 'Not a PAN card')."
    )
    extraction_data: Optional[PanExtractionSchema] = Field(None, description="The extracted data if is_error is false.")


class AadharExtractionResponse(BaseModel):
    is_error: bool = Field(description="True if the provided image is NOT a valid Aadhar card.")
    error_message: Optional[str] = Field(
        None, description="If is_error is true, describe why (e.g. 'Image too blurry', 'Not an Aadhar card')."
    )
    extraction_data: Optional[AadharExtractionSchema] = Field(None, description="The extracted data if is_error is false.")


class BatchExtractionInitiatedResponse(BaseModel):
    batch_id: str
    message: str = "Batch extraction initiated in the background."


class DocumentStatusResponse(BaseModel):
    id: str
    batch_id: str
    doc_type: Optional[str] = None
    status: str  # queued, extracting, completed, error
    error_message: Optional[str] = None
    extraction_data: Optional[dict] = None
    created_at: str


class BatchStatusResponse(BaseModel):
    batch_id: str
    documents: List[DocumentStatusResponse]
    is_completed: bool
