"""
Security utilities for JurisLink backend.
Handles JWT token generation/verification and password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from .config import settings


# Password hashing context
# Note: using PBKDF2 which doesn't have Windows bcrypt library issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode (user_id, role, email)
        expires_delta: Optional token expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and extract claims.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        Decoded token payload with user_id, role, email
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    token = credentials.credentials
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def require_role(*allowed_roles: str):
    """
    Factory function that creates a dependency to check if user has required role.
    
    Args:
        allowed_roles: Tuple of allowed role strings (e.g., "admin", "lawyer")
        
    Returns:
        Async dependency function that checks user role
        
    Raises:
        HTTPException: 403 if user role is not in allowed_roles
    """
    async def check_role(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this resource"
            )
        return current_user
    
    return check_role
