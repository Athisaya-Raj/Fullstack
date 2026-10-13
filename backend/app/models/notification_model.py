"""
Pydantic models for Notification resource.
Defines request/response schemas for user notifications.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Valid notification types."""
    CASE_ASSIGNED = "case_assigned"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    APPOINTMENT_REMINDER = "appointment_reminder"
    CASE_STATUS_UPDATED = "case_status_updated"
    DOCUMENT_PROCESSED = "document_processed"
    MESSAGE = "message"


class NotificationCreate(BaseModel):
    """Schema for creating a new notification."""
    user_id: str = Field(...)
    case_id: Optional[str] = None
    notification_type: NotificationType = Field(...)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)


class NotificationOut(BaseModel):
    """Schema for notification response data."""
    notification_id: str
    user_id: str
    case_id: Optional[str] = None
    notification_type: NotificationType
    title: str
    message: str
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
