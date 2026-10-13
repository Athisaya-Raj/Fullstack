"""
Pydantic models for Case Update (Case History) resource.
Defines schemas for tracking case status changes and updates.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CaseUpdateCreate(BaseModel):
    """Schema for creating a case update."""
    case_id: str = Field(...)
    updated_by: str = Field(..., description="ID of the user who made the update")
    previous_status: Optional[str] = None
    new_status: str = Field(...)
    comment: Optional[str] = Field(None, max_length=500)


class CaseUpdateOut(BaseModel):
    """Schema for case update response data."""
    update_id: str
    case_id: str
    updated_by: str
    previous_status: Optional[str] = None
    new_status: str
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
