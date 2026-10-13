"""
Pydantic models for Document resource.
Defines request/response schemas for document upload and management.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    """Schema for uploading a new document."""
    case_id: str = Field(..., description="ID of the case this document belongs to")
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., description="e.g., 'application/pdf', 'image/jpeg'")


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""
    extracted_text: Optional[str] = None
    summary: Optional[str] = None


class DocumentOut(BaseModel):
    """Schema for document response data."""
    document_id: str
    case_id: str
    user_id: str
    file_name: str
    file_type: str
    file_path: str
    file_size: int
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    uploaded_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
