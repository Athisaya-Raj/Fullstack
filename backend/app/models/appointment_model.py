"""
Pydantic models for Appointment resource.
Defines request/response schemas for appointment booking and management.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    """Valid appointment statuses."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment."""
    case_id: str = Field(..., description="ID of the case")
    lawyer_id: str = Field(..., description="ID of the lawyer")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(default=30, ge=15, le=300)
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment."""
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=300)
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    """Schema for appointment response data."""
    appointment_id: str
    case_id: str
    user_id: str
    lawyer_id: str
    appointment_date: datetime
    duration_minutes: int
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
