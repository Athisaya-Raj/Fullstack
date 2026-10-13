"""
Pydantic models for Legal QA resource.
Defines schemas for Legal Question & Answer dataset from IndicLegalQA.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LegalQACreate(BaseModel):
    """Schema for creating a legal Q&A record."""
    question: str = Field(..., min_length=5, max_length=1000)
    answer: str = Field(..., min_length=10, max_length=5000)
    case_reference: Optional[str] = None
    case_name: Optional[str] = None
    legal_category: Optional[str] = None
    source: str = Field(default="IndicLegalQA")


class LegalQAOut(BaseModel):
    """Schema for legal QA response data."""
    qa_id: str
    question: str
    answer: str
    case_reference: Optional[str] = None
    case_name: Optional[str] = None
    legal_category: Optional[str] = None
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LegalQASearch(BaseModel):
    """Schema for legal QA search request."""
    query: str = Field(..., description="Search query")
    legal_category: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
    skip: int = Field(default=0, ge=0)
