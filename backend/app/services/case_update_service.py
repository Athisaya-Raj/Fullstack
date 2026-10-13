"""
Case Update Service for JurisLink.
Maintains the history of changes to a case.
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.case_update_model import CaseUpdateCreate, CaseUpdateOut
from ..db.mongodb import get_database


class CaseUpdateService:
    """Service for managing case update history."""
    
    def __init__(self):
        self.db = None
        self.collection_name = "case_updates"
    
    def _get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_case_update(
        self,
        update_data: CaseUpdateCreate
    ) -> CaseUpdateOut:
        """Create a new case update record."""
        db = self._get_db()
        
        update_doc = {
            "case_id": ObjectId(update_data.case_id),
            "updated_by": ObjectId(update_data.updated_by),
            "previous_status": update_data.previous_status,
            "new_status": update_data.new_status,
            "comment": update_data.comment,
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(update_doc)
        update_doc["_id"] = result.inserted_id
        
        return self._format_case_update_out(update_doc)
    
    async def get_case_timeline(self, case_id: str) -> List[CaseUpdateOut]:
        """Get the timeline of updates for a case."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"case_id": ObjectId(case_id)}
        ).sort("created_at", 1)
        
        updates = []
        async for update in cursor:
            updates.append(self._format_case_update_out(update))
        
        return updates
    
    async def get_latest_update(self, case_id: str) -> Optional[CaseUpdateOut]:
        """Get the latest update for a case."""
        try:
            db = self._get_db()
            update = await db[self.collection_name].find_one(
                {"case_id": ObjectId(case_id)},
                sort=[("created_at", -1)]
            )
            
            if update:
                return self._format_case_update_out(update)
            return None
        except Exception:
            return None
    
    def _format_case_update_out(self, update_doc: dict) -> CaseUpdateOut:
        """Convert MongoDB update document to CaseUpdateOut."""
        return CaseUpdateOut(
            update_id=str(update_doc["_id"]),
            case_id=str(update_doc["case_id"]),
            updated_by=str(update_doc["updated_by"]),
            previous_status=update_doc.get("previous_status"),
            new_status=update_doc["new_status"],
            comment=update_doc.get("comment"),
            created_at=update_doc["created_at"],
        )
