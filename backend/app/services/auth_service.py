"""
Auth Service for JurisLink.
Handles user registration, authentication, and user queries.
"""
from datetime import timedelta, datetime, timezone
from typing import Optional
from bson import ObjectId
from ..models.user_model import UserCreate, UserOut
from ..core.security import hash_password, verify_password, create_access_token
from ..db.mongodb import get_database


class AuthService:
    """Service for user authentication and management."""
    
    def __init__(self):
        """Initialize auth service."""
        self.db = None  # Lazy load database
        self.collection_name = "users"
    
    def _get_db(self):
        """Get database, lazy loading."""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def user_exists(self, email: str) -> bool:
        """
        Check if a user with given email already exists.
        
        Args:
            email: Email address to check
            
        Returns:
            True if user exists, False otherwise
        """
        db = self._get_db()
        user = await db[self.collection_name].find_one({"email": email})
        return user is not None
    
    async def create_user(self, user_create: UserCreate) -> UserOut:
        """
        Create a new user with hashed password.
        
        Args:
            user_create: User creation request with email, full_name, password, role
            
        Returns:
            UserOut with created user data (password hash never included)
            
        Raises:
            Exception: If email already exists
        """
        # Check if user already exists
        if await self.user_exists(user_create.email):
            raise Exception(f"User with email {user_create.email} already exists")
        
        # Create user document
        user_doc = {
            "email": user_create.email,
            "full_name": user_create.full_name,
            "hashed_password": hash_password(user_create.password),
            "role": user_create.role,
            "is_verified": True if user_create.role != "lawyer" else False,  # Lawyers start unverified
            "created_at": datetime.now(timezone.utc),
        }
        
        # Insert into database
        db = self._get_db()
        result = await db[self.collection_name].insert_one(user_doc)
        
        # Fetch and return created user
        created_user = await db[self.collection_name].find_one(
            {"_id": result.inserted_id}
        )
        
        return self._format_user_out(created_user)
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Get user document from database by email.
        
        Args:
            email: User email
            
        Returns:
            User document if found, None otherwise
        """
        db = self._get_db()
        user = await db[self.collection_name].find_one({"email": email})
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserOut]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID (MongoDB ObjectId as string)
            
        Returns:
            UserOut if found, None otherwise
        """
        try:
            db = self._get_db()
            user = await db[self.collection_name].find_one(
                {"_id": ObjectId(user_id)}
            )
            if user:
                return self._format_user_out(user)
            return None
        except Exception:
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User document if credentials valid, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.get("hashed_password", "")):
            return None
        
        return user
    
    async def create_token_for_user(self, user_doc: dict) -> str:
        """
        Create JWT access token for authenticated user.
        
        Args:
            user_doc: User document from MongoDB
            
        Returns:
            JWT access token string
        """
        token_data = {
            "user_id": str(user_doc["_id"]),
            "role": user_doc["role"],
            "email": user_doc["email"],
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )
        
        return access_token
    
    def _format_user_out(self, user_doc: dict) -> UserOut:
        """
        Convert MongoDB user document to UserOut (remove sensitive fields).
        
        Args:
            user_doc: Raw user document from MongoDB
            
        Returns:
            UserOut with formatted user data
        """
        return UserOut(
            user_id=str(user_doc["_id"]),
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            role=user_doc["role"],
            is_verified=user_doc.get("is_verified"),
            created_at=user_doc.get("created_at")
        )
