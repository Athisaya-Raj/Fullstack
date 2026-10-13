"""
Pydantic models for Case resource.
Defines request/response schemas for legal case intake and management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CaseStatus(str, Enum):
    """Valid case statuses."""
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    ASSIGNED = "Assigned"
    APPOINTMENT_SCHEDULED = "Appointment Scheduled"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class CaseCreate(BaseModel):
    """Schema for creating a new case."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)


class CaseUpdate(BaseModel):
    """Schema for updating a case."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = Field(None, description="Low | Medium | High")
    status: Optional[CaseStatus] = None
    lawyer_id: Optional[str] = None


class CaseStatusUpdate(BaseModel):
    """Schema for updating case status (lawyer/admin only)."""
    status: CaseStatus


class CaseOut(BaseModel):
    """Schema for case response data."""
    case_id: str
    user_id: str
    title: str
    description: str
    predicted_category: Optional[str] = None
    priority: Optional[str] = None
    status: CaseStatus
    lawyer_id: Optional[str] = None
    documents: List[str] = Field(default=[], description="List of document IDs")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
