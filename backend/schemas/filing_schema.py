from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.constants import DocumentType, ITRType

class FilingDocumentSchema(BaseModel):
    name: str = Field(..., description="Original filename")
    type: DocumentType = Field(..., description="Enum: AS26, AIS, etc.")
    is_extraction_complete: bool = False
    total_pages: int = 0

class FilingAttemptBase(BaseModel):
    assessment_year: str = Field(..., description="Format: AY-YYYY-YY")
    itr_type: ITRType = Field(..., description="ITR-1, ITR-2, etc.")
    documents: List[FilingDocumentSchema] = []

class FilingAttemptCreate(FilingAttemptBase):
    user_id: str

class FilingAttemptResponse(FilingAttemptBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return None
        data["_id"] = str(data["_id"])
        data["user_id"] = str(data["user_id"])
        return cls(**data)
