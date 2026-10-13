"""
Document management routes for JurisLink.
Endpoints for document upload, retrieval, and management.
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List
import os
from ..models.document_model import DocumentCreate, DocumentUpdate, DocumentOut
from ..services.document_service import DocumentService
from ..core.security import get_current_user


router = APIRouter(prefix="/documents", tags=["documents"])
document_service = None

# File upload configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_document_service():
    """Get or initialize document service."""
    global document_service
    if document_service is None:
        document_service = DocumentService()
    return document_service


def ensure_upload_dir():
    """Ensure upload directory exists."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document to a case."""
    try:
        # Validate file
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum ({MAX_FILE_SIZE} bytes)"
            )
        
        ensure_upload_dir()
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, f"{case_id}_{file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create document record
        service = get_document_service()
        document_data = DocumentCreate(
            case_id=case_id,
            file_name=file.filename,
            file_type=file.content_type or "application/octet-stream"
        )
        
        document = await service.create_document(
            case_id=case_id,
            user_id=current_user["user_id"],
            document_data=document_data,
            file_path=file_path,
            file_size=len(content)
        )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get document metadata."""
    try:
        service = get_document_service()
        document = await service.get_document_by_id(document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=List[DocumentOut])
async def list_case_documents(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List all documents for a case."""
    try:
        service = get_document_service()
        documents = await service.get_documents_by_case(case_id)
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{document_id}", response_model=DocumentOut)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update document metadata (extracted text, summary)."""
    try:
        service = get_document_service()
        updated = await service.update_document(document_id, update_data)
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document."""
    try:
        service = get_document_service()
        success = await service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
