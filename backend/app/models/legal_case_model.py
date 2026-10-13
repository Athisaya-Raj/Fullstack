"""
Pydantic models for Legal Case resource.
Defines schemas for Indian Supreme Court legal cases (public legal knowledge).
NOTE: This is different from the 'cases' collection which stores user cases.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LegalCaseCreate(BaseModel):
    """Schema for creating a legal case record."""
    source: str = Field(default="Supreme Court of India")
    source_case_id: str = Field(..., description="Unique ID from the source dataset")
    case_title: str = Field(..., min_length=5, max_length=500)
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    judgment_date: Optional[datetime] = None
    judges: List[str] = Field(default=[])
    citation: Optional[str] = None
    case_type: Optional[str] = None
    legal_category: Optional[str] = None
    judgment_text: str = Field(..., description="Full judgment text")
    disposal_nature: Optional[str] = None
    summary: Optional[str] = None


class LegalCaseOut(BaseModel):
    """Schema for legal case response data."""
    legal_case_id: str
    source: str
    source_case_id: str
    case_title: str
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    judgment_date: Optional[datetime] = None
    judges: List[str]
    citation: Optional[str] = None
    case_type: Optional[str] = None
    legal_category: Optional[str] = None
    judgment_text: str
    disposal_nature: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LegalCaseSearch(BaseModel):
    """Schema for legal case search request."""
    query: Optional[str] = Field(None, description="Free text search query")
    legal_category: Optional[str] = None
    case_type: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    skip: int = Field(default=0, ge=0)
