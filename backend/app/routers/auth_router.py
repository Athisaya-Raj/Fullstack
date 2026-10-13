"""
Authentication router for JurisLink.
Handles user registration, login, and token management.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from ..models.user_model import UserCreate, UserLogin, UserOut, TokenResponse
from ..services.auth_service import AuthService
from ..core.security import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = None  # Lazy initialization


def get_auth_service():
    """Get or initialize auth service."""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate):
    """
    Register a new user.
    
    Args:
        user_create: User registration data (email, full_name, password, role)
        
    Returns:
        Created user data (UserOut - no password hash)
        
    Raises:
        HTTPException: 400 if email already exists
    """
    try:
        service = get_auth_service()
        user = await service.create_user(user_create)
        return user
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login a user and return access token.
    
    Args:
        credentials: Email and password for login
        
    Returns:
        TokenResponse with access_token and user data
        
    Raises:
        HTTPException: 401 if credentials invalid
    """
    service = get_auth_service()
    # Authenticate user
    user_doc = await service.authenticate_user(
        credentials.email,
        credentials.password
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if lawyer is verified
    if user_doc.get("role") == "lawyer" and not user_doc.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your lawyer account is pending verification by an admin"
        )
    
    # Create access token
    access_token = await service.create_token_for_user(user_doc)
    
    # Format user for response
    user_out = service._format_user_out(user_doc)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_out
    )


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current logged-in user's profile.
    
    Used by frontend to restore session on page refresh.
    Requires valid JWT token in Authorization: Bearer header.
    
    Args:
        current_user: Current user from JWT token (via dependency)
        
    Returns:
        Current user data (UserOut)
        
    Raises:
        HTTPException: 401 if token invalid/expired
    """
    # Get full user document from database
    service = get_auth_service()
    user = await service.get_user_by_id(current_user.get("user_id"))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
