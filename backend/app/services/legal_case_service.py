"""
Legal Case Service for JurisLink.
Handles Indian Supreme Court legal cases (public legal knowledge).
NOTE: This is different from the 'cases' service which handles user cases.
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.legal_case_model import LegalCaseCreate, LegalCaseOut, LegalCaseSearch
from ..db.mongodb import get_database


class LegalCaseService:
    """Service for managing legal case knowledge base."""
    
    def __init__(self):
        self.db = None
        self.collection_name = "legal_cases"
    
    def _get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_legal_case(
        self,
        legal_case_data: LegalCaseCreate
    ) -> LegalCaseOut:
        """Create a new legal case record."""
        db = self._get_db()
        
        case_doc = {
            "source": legal_case_data.source,
            "source_case_id": legal_case_data.source_case_id,
            "case_title": legal_case_data.case_title,
            "petitioner": legal_case_data.petitioner,
            "respondent": legal_case_data.respondent,
            "judgment_date": legal_case_data.judgment_date,
            "judges": legal_case_data.judges,
            "citation": legal_case_data.citation,
            "case_type": legal_case_data.case_type,
            "legal_category": legal_case_data.legal_category,
            "judgment_text": legal_case_data.judgment_text,
            "disposal_nature": legal_case_data.disposal_nature,
            "summary": legal_case_data.summary,
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(case_doc)
        case_doc["_id"] = result.inserted_id
        
        return self._format_legal_case_out(case_doc)
    
    async def get_legal_case_by_id(self, legal_case_id: str) -> Optional[LegalCaseOut]:
        """Retrieve a legal case by ID."""
        try:
            db = self._get_db()
            case = await db[self.collection_name].find_one(
                {"_id": ObjectId(legal_case_id)}
            )
            if case:
                return self._format_legal_case_out(case)
            return None
        except Exception:
            return None
    
    async def search_legal_cases(
        self,
        search_params: LegalCaseSearch
    ) -> List[LegalCaseOut]:
        """Search legal cases."""
        db = self._get_db()
        query = {}
        
        if search_params.query:
            # Full text search on case title and judgment text
            query["$or"] = [
                {"case_title": {"$regex": search_params.query, "$options": "i"}},
                {"judgment_text": {"$regex": search_params.query, "$options": "i"}},
            ]
        
        if search_params.legal_category:
            query["legal_category"] = search_params.legal_category
        
        if search_params.case_type:
            query["case_type"] = search_params.case_type
        
        cursor = db[self.collection_name].find(query).skip(
            search_params.skip
        ).limit(search_params.limit)
        
        cases = []
        async for case in cursor:
            cases.append(self._format_legal_case_out(case))
        
        return cases
    
    async def get_cases_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[LegalCaseOut]:
        """Get legal cases by category."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"legal_category": category}
        ).skip(skip).limit(limit)
        
        cases = []
        async for case in cursor:
            cases.append(self._format_legal_case_out(case))
        
        return cases
    
    async def get_total_count(self) -> int:
        """Get total number of legal cases in the database."""
        try:
            db = self._get_db()
            count = await db[self.collection_name].count_documents({})
            return count
        except Exception:
            return 0
    
    def _format_legal_case_out(self, case_doc: dict) -> LegalCaseOut:
        """Convert MongoDB case document to LegalCaseOut."""
        return LegalCaseOut(
            legal_case_id=str(case_doc["_id"]),
            source=case_doc.get("source", "Supreme Court of India"),
            source_case_id=case_doc["source_case_id"],
            case_title=case_doc["case_title"],
            petitioner=case_doc.get("petitioner"),
            respondent=case_doc.get("respondent"),
            judgment_date=case_doc.get("judgment_date"),
            judges=case_doc.get("judges", []),
            citation=case_doc.get("citation"),
            case_type=case_doc.get("case_type"),
            legal_category=case_doc.get("legal_category"),
            judgment_text=case_doc["judgment_text"],
            disposal_nature=case_doc.get("disposal_nature"),
            summary=case_doc.get("summary"),
            created_at=case_doc["created_at"],
        )
