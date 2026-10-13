"""
Legal QA Service for JurisLink.
Handles Legal Question & Answer dataset from IndicLegalQA.
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.legal_qa_model import LegalQACreate, LegalQAOut, LegalQASearch
from ..db.mongodb import get_database


class LegalQAService:
    """Service for managing legal Q&A knowledge base."""
    
    def __init__(self):
        self.db = None
        self.collection_name = "legal_qa"
    
    def _get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_legal_qa(
        self,
        qa_data: LegalQACreate
    ) -> LegalQAOut:
        """Create a new legal Q&A record."""
        db = self._get_db()
        
        qa_doc = {
            "question": qa_data.question,
            "answer": qa_data.answer,
            "case_reference": qa_data.case_reference,
            "case_name": qa_data.case_name,
            "legal_category": qa_data.legal_category,
            "source": qa_data.source,
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(qa_doc)
        qa_doc["_id"] = result.inserted_id
        
        return self._format_legal_qa_out(qa_doc)
    
    async def get_legal_qa_by_id(self, qa_id: str) -> Optional[LegalQAOut]:
        """Retrieve a legal Q&A by ID."""
        try:
            db = self._get_db()
            qa = await db[self.collection_name].find_one(
                {"_id": ObjectId(qa_id)}
            )
            if qa:
                return self._format_legal_qa_out(qa)
            return None
        except Exception:
            return None
    
    async def search_legal_qa(
        self,
        search_params: LegalQASearch
    ) -> List[LegalQAOut]:
        """Search legal Q&A."""
        db = self._get_db()
        query = {}
        
        if search_params.query:
            # Full text search on question and answer
            query["$or"] = [
                {"question": {"$regex": search_params.query, "$options": "i"}},
                {"answer": {"$regex": search_params.query, "$options": "i"}},
            ]
        
        if search_params.legal_category:
            query["legal_category"] = search_params.legal_category
        
        cursor = db[self.collection_name].find(query).skip(
            search_params.skip
        ).limit(search_params.limit)
        
        results = []
        async for qa in cursor:
            results.append(self._format_legal_qa_out(qa))
        
        return results
    
    async def get_qa_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[LegalQAOut]:
        """Get Q&A by legal category."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"legal_category": category}
        ).skip(skip).limit(limit)
        
        results = []
        async for qa in cursor:
            results.append(self._format_legal_qa_out(qa))
        
        return results
    
    async def get_total_count(self) -> int:
        """Get total number of legal Q&A in the database."""
        try:
            db = self._get_db()
            count = await db[self.collection_name].count_documents({})
            return count
        except Exception:
            return 0
    
    def _format_legal_qa_out(self, qa_doc: dict) -> LegalQAOut:
        """Convert MongoDB Q&A document to LegalQAOut."""
        return LegalQAOut(
            qa_id=str(qa_doc["_id"]),
            question=qa_doc["question"],
            answer=qa_doc["answer"],
            case_reference=qa_doc.get("case_reference"),
            case_name=qa_doc.get("case_name"),
            legal_category=qa_doc.get("legal_category"),
            source=qa_doc.get("source", "IndicLegalQA"),
            created_at=qa_doc["created_at"],
        )
