"""
Pydantic models for Lawyer resource.
Defines request/response schemas for lawyer profile management.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class LawyerCreate(BaseModel):
    """Schema for creating a new lawyer profile."""
    name: str = Field(..., min_length=3, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    specializations: List[str] = Field(default=[], description="e.g., ['Civil Law', 'Property Law']")
    experience_years: int = Field(..., ge=0, le=70)
    location: str = Field(..., min_length=3, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    availability: bool = Field(default=True)


class LawyerUpdate(BaseModel):
    """Schema for updating lawyer profile."""
    specializations: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=70)
    location: Optional[str] = None
    bio: Optional[str] = None
    availability: Optional[bool] = None


class LawyerOut(BaseModel):
    """Schema for lawyer response data."""
    lawyer_id: str
    user_id: str
    name: str
    email: str
    phone: str
    specializations: List[str]
    experience_years: int
    location: str
    bio: Optional[str] = None
    availability: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
