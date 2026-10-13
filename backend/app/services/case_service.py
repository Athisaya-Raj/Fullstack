"""
Case Service for JurisLink.
Handles user case creation, retrieval, and status updates.
NOTE: This handles USER cases, not public legal cases (see legal_case_service).
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.case_model import CaseCreate, CaseUpdate, CaseStatusUpdate, CaseOut, CaseStatus
from ..db.mongodb import get_database


class CaseService:
    """Service for managing user legal cases."""
    
    def __init__(self):
        """Initialize case service."""
        self.db = None
        self.collection_name = "cases"
    
    def _get_db(self):
        """Get database, lazy loading."""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_case(
        self,
        user_id: str,
        case_data: CaseCreate,
        predicted_category: Optional[str] = None
    ) -> CaseOut:
        """
        Create a new user case.
        
        Args:
            user_id: ID of the user creating the case
            case_data: Case creation request
            predicted_category: Optional category from NLP classification
            
        Returns:
            Created case with metadata
        """
        db = self._get_db()
        
        case_doc = {
            "user_id": ObjectId(user_id),
            "lawyer_id": None,
            "title": case_data.title,
            "description": case_data.description,
            "predicted_category": predicted_category,
            "priority": "Medium",  # Default priority
            "status": CaseStatus.SUBMITTED.value,
            "documents": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(case_doc)
        case_doc["_id"] = result.inserted_id
        
        return self._format_case_out(case_doc)
    
    async def get_case_by_id(self, case_id: str) -> Optional[CaseOut]:
        """Retrieve a case by ID."""
        try:
            db = self._get_db()
            case = await db[self.collection_name].find_one(
                {"_id": ObjectId(case_id)}
            )
            if case:
                return self._format_case_out(case)
            return None
        except Exception:
            return None
    
    async def get_user_cases(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[CaseOut]:
        """Get all cases for a user."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        cases = []
        async for case in cursor:
            cases.append(self._format_case_out(case))
        
        return cases
    
    async def get_cases_assigned_to_lawyer(
        self,
        lawyer_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[CaseOut]:
        """Get all cases assigned to a lawyer."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"lawyer_id": ObjectId(lawyer_id)}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        cases = []
        async for case in cursor:
            cases.append(self._format_case_out(case))
        
        return cases
    
    async def update_case(
        self,
        case_id: str,
        update_data: CaseUpdate
    ) -> Optional[CaseOut]:
        """Update case details."""
        try:
            db = self._get_db()
            
            update_dict = {"updated_at": datetime.now(timezone.utc)}
            
            if update_data.title is not None:
                update_dict["title"] = update_data.title
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.priority is not None:
                update_dict["priority"] = update_data.priority
            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            if update_data.lawyer_id is not None:
                update_dict["lawyer_id"] = ObjectId(update_data.lawyer_id)
            
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(case_id)},
                {"$set": update_dict},
                return_document=True
            )
            
            if result:
                return self._format_case_out(result)
            return None
        except Exception:
            return None
    
    async def update_case_status(
        self,
        case_id: str,
        status_update: CaseStatusUpdate
    ) -> Optional[CaseOut]:
        """Update only the case status."""
        try:
            db = self._get_db()
            
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(case_id)},
                {
                    "$set": {
                        "status": status_update.status.value,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                return_document=True
            )
            
            if result:
                return self._format_case_out(result)
            return None
        except Exception:
            return None
    
    async def assign_case_to_lawyer(
        self,
        case_id: str,
        lawyer_id: str
    ) -> Optional[CaseOut]:
        """Assign a case to a lawyer."""
        try:
            db = self._get_db()
            
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(case_id)},
                {
                    "$set": {
                        "lawyer_id": ObjectId(lawyer_id),
                        "status": CaseStatus.ASSIGNED.value,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                return_document=True
            )
            
            if result:
                return self._format_case_out(result)
            return None
        except Exception:
            return None
    
    async def add_document_to_case(
        self,
        case_id: str,
        document_id: str
    ) -> Optional[CaseOut]:
        """Add a document ID to a case's documents list."""
        try:
            db = self._get_db()
            
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(case_id)},
                {
                    "$push": {"documents": ObjectId(document_id)},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                },
                return_document=True
            )
            
            if result:
                return self._format_case_out(result)
            return None
        except Exception:
            return None
    
    async def delete_case(self, case_id: str) -> bool:
        """Delete a case (soft delete recommended in production)."""
        try:
            db = self._get_db()
            result = await db[self.collection_name].delete_one(
                {"_id": ObjectId(case_id)}
            )
            return result.deleted_count > 0
        except Exception:
            return False
    
    def _format_case_out(self, case_doc: dict) -> CaseOut:
        """Convert MongoDB case document to CaseOut."""
        return CaseOut(
            case_id=str(case_doc["_id"]),
            user_id=str(case_doc["user_id"]),
            title=case_doc["title"],
            description=case_doc["description"],
            predicted_category=case_doc.get("predicted_category"),
            priority=case_doc.get("priority", "Medium"),
            status=case_doc["status"],
            lawyer_id=str(case_doc["lawyer_id"]) if case_doc.get("lawyer_id") else None,
            documents=[str(doc_id) for doc_id in case_doc.get("documents", [])],
            created_at=case_doc.get("created_at"),
            updated_at=case_doc.get("updated_at"),
        )
