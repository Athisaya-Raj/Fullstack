"""
Lawyer Service for JurisLink.
Handles lawyer profile creation, retrieval, and management.
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.lawyer_model import LawyerCreate, LawyerUpdate, LawyerOut
from ..db.mongodb import get_database


class LawyerService:
    """Service for managing lawyer profiles."""
    
    def __init__(self):
        """Initialize lawyer service."""
        self.db = None
        self.collection_name = "lawyers"
    
    def _get_db(self):
        """Get database, lazy loading."""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_lawyer(
        self,
        user_id: str,
        email: str,
        lawyer_data: LawyerCreate
    ) -> LawyerOut:
        """Create a new lawyer profile."""
        db = self._get_db()
        
        lawyer_doc = {
            "user_id": ObjectId(user_id),
            "name": lawyer_data.name,
            "email": email,
            "phone": lawyer_data.phone,
            "specializations": lawyer_data.specializations,
            "experience_years": lawyer_data.experience_years,
            "location": lawyer_data.location,
            "bio": lawyer_data.bio,
            "availability": lawyer_data.availability,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(lawyer_doc)
        lawyer_doc["_id"] = result.inserted_id
        
        return self._format_lawyer_out(lawyer_doc)
    
    async def get_lawyer_by_id(self, lawyer_id: str) -> Optional[LawyerOut]:
        """Retrieve a lawyer by ID."""
        try:
            db = self._get_db()
            lawyer = await db[self.collection_name].find_one(
                {"_id": ObjectId(lawyer_id)}
            )
            if lawyer:
                return self._format_lawyer_out(lawyer)
            return None
        except Exception:
            return None
    
    async def get_lawyer_by_user_id(self, user_id: str) -> Optional[LawyerOut]:
        """Retrieve a lawyer by user ID."""
        try:
            db = self._get_db()
            lawyer = await db[self.collection_name].find_one(
                {"user_id": ObjectId(user_id)}
            )
            if lawyer:
                return self._format_lawyer_out(lawyer)
            return None
        except Exception:
            return None
    
    async def get_all_lawyers(self, skip: int = 0, limit: int = 50) -> List[LawyerOut]:
        """Retrieve all available lawyers."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"availability": True}
        ).skip(skip).limit(limit)
        
        lawyers = []
        async for lawyer in cursor:
            lawyers.append(self._format_lawyer_out(lawyer))
        
        return lawyers
    
    async def search_lawyers(
        self,
        specialization: Optional[str] = None,
        location: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[LawyerOut]:
        """Search lawyers by specialization and/or location."""
        db = self._get_db()
        query = {"availability": True}
        
        if specialization:
            query["specializations"] = specialization
        
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit)
        
        lawyers = []
        async for lawyer in cursor:
            lawyers.append(self._format_lawyer_out(lawyer))
        
        return lawyers
    
    async def update_lawyer(
        self,
        lawyer_id: str,
        update_data: LawyerUpdate
    ) -> Optional[LawyerOut]:
        """Update lawyer profile."""
        try:
            db = self._get_db()
            
            update_dict = {"updated_at": datetime.now(timezone.utc)}
            
            if update_data.specializations is not None:
                update_dict["specializations"] = update_data.specializations
            if update_data.experience_years is not None:
                update_dict["experience_years"] = update_data.experience_years
            if update_data.location is not None:
                update_dict["location"] = update_data.location
            if update_data.bio is not None:
                update_dict["bio"] = update_data.bio
            if update_data.availability is not None:
                update_dict["availability"] = update_data.availability
            
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(lawyer_id)},
                {"$set": update_dict},
                return_document=True
            )
            
            if result:
                return self._format_lawyer_out(result)
            return None
        except Exception:
            return None
    
    def _format_lawyer_out(self, lawyer_doc: dict) -> LawyerOut:
        """Convert MongoDB lawyer document to LawyerOut."""
        return LawyerOut(
            lawyer_id=str(lawyer_doc["_id"]),
            user_id=str(lawyer_doc["user_id"]),
            name=lawyer_doc["name"],
            email=lawyer_doc["email"],
            phone=lawyer_doc["phone"],
            specializations=lawyer_doc.get("specializations", []),
            experience_years=lawyer_doc.get("experience_years", 0),
            location=lawyer_doc["location"],
            bio=lawyer_doc.get("bio"),
            availability=lawyer_doc.get("availability", True),
            created_at=lawyer_doc.get("created_at"),
            updated_at=lawyer_doc.get("updated_at"),
        )
