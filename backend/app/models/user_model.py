"""
Pydantic models for User resource.
Defines request/response schemas for authentication and user management.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user fields shared across schemas."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for creating a new user (signup)."""
    password: str
    role: str = Field(default="client", description="Role: client, lawyer, or admin")


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class UserOut(UserBase):
    """Schema for user response data (never includes password hash)."""
    user_id: str
    role: str
    is_verified: Optional[bool] = None  # For lawyers only
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response after successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    """Schema for JWT payload data."""
    user_id: str
    role: str
    email: EmailStr
