"""
Document Service for JurisLink.
Handles document upload, storage metadata, and retrieval.
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.document_model import DocumentCreate, DocumentUpdate, DocumentOut
from ..db.mongodb import get_database


class DocumentService:
    """Service for managing case documents."""
    
    def __init__(self):
        """Initialize document service."""
        self.db = None
        self.collection_name = "documents"
    
    def _get_db(self):
        """Get database, lazy loading."""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_document(
        self,
        case_id: str,
        user_id: str,
        document_data: DocumentCreate,
        file_path: str,
        file_size: int
    ) -> DocumentOut:
        """Create a new document record."""
        db = self._get_db()
        
        document_doc = {
            "case_id": ObjectId(case_id),
            "user_id": ObjectId(user_id),
            "file_name": document_data.file_name,
            "file_type": document_data.file_type,
            "file_path": file_path,
            "file_size": file_size,
            "extracted_text": None,
            "summary": None,
            "uploaded_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(document_doc)
        document_doc["_id"] = result.inserted_id
        
        return self._format_document_out(document_doc)
    
    async def get_document_by_id(self, document_id: str) -> Optional[DocumentOut]:
        """Retrieve a document by ID."""
        try:
            db = self._get_db()
            document = await db[self.collection_name].find_one(
                {"_id": ObjectId(document_id)}
            )
            if document:
                return self._format_document_out(document)
            return None
        except Exception:
            return None
    
    async def get_documents_by_case(self, case_id: str) -> List[DocumentOut]:
        """Retrieve all documents for a case."""
        try:
            db = self._get_db()
            cursor = db[self.collection_name].find(
                {"case_id": ObjectId(case_id)}
            ).sort("uploaded_at", -1)
            
            documents = []
            async for document in cursor:
                documents.append(self._format_document_out(document))
            
            return documents
        except Exception:
            return []
    
    async def update_document(
        self,
        document_id: str,
        update_data: DocumentUpdate
    ) -> Optional[DocumentOut]:
        """Update document metadata."""
        try:
            db = self._get_db()
            
            update_dict = {"updated_at": datetime.now(timezone.utc)}
            
            if update_data.extracted_text is not None:
                update_dict["extracted_text"] = update_data.extracted_text
            if update_data.summary is not None:
                update_dict["summary"] = update_data.summary
            
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(document_id)},
                {"$set": update_dict},
                return_document=True
            )
            
            if result:
                return self._format_document_out(result)
            return None
        except Exception:
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document record."""
        try:
            db = self._get_db()
            result = await db[self.collection_name].delete_one(
                {"_id": ObjectId(document_id)}
            )
            return result.deleted_count > 0
        except Exception:
            return False
    
    def _format_document_out(self, document_doc: dict) -> DocumentOut:
        """Convert MongoDB document to DocumentOut."""
        return DocumentOut(
            document_id=str(document_doc["_id"]),
            case_id=str(document_doc["case_id"]),
            user_id=str(document_doc["user_id"]),
            file_name=document_doc["file_name"],
            file_type=document_doc["file_type"],
            file_path=document_doc["file_path"],
            file_size=document_doc.get("file_size", 0),
            extracted_text=document_doc.get("extracted_text"),
            summary=document_doc.get("summary"),
            uploaded_at=document_doc.get("uploaded_at"),
            updated_at=document_doc.get("updated_at"),
        )
