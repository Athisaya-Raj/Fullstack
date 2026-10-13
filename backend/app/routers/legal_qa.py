"""
Legal Q&A routes for JurisLink.
Endpoints for searching and retrieving legal Q&A records.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from ..models.legal_qa_model import LegalQAOut, LegalQASearch
from ..services.legal_qa_service import LegalQAService


router = APIRouter(prefix="/legal/qa", tags=["legal-qa"])
legal_qa_service = None


def get_legal_qa_service():
    global legal_qa_service
    if legal_qa_service is None:
        legal_qa_service = LegalQAService()
    return legal_qa_service


@router.get("/search", response_model=List[LegalQAOut])
async def search_legal_qa(
    query: Optional[str] = Query(None, description="Search query"),
    legal_category: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    """Search legal Q&A from IndicLegalQA database."""
    try:
        service = get_legal_qa_service()
        
        search_params = LegalQASearch(
            query=query,
            legal_category=legal_category,
            skip=skip,
            limit=limit
        )
        
        qa_results = await service.search_legal_qa(search_params)
        return qa_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{qa_id}", response_model=LegalQAOut)
async def get_legal_qa(qa_id: str):
    """Get a specific legal Q&A record."""
    try:
        service = get_legal_qa_service()
        qa = await service.get_legal_qa_by_id(qa_id)
        
        if not qa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal Q&A record not found"
            )
        
        return qa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/category/{category}", response_model=List[LegalQAOut])
async def get_qa_by_category(
    category: str,
    skip: int = 0,
    limit: int = 50
):
    """Get legal Q&A by legal category."""
    try:
        service = get_legal_qa_service()
        qa_results = await service.get_qa_by_category(
            category=category,
            skip=skip,
            limit=limit
        )
        return qa_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_legal_qa_stats():
    """Get statistics about the legal Q&A database."""
    try:
        service = get_legal_qa_service()
        total_qa = await service.get_total_count()
        
        return {
            "total_qa_records": total_qa,
            "source": "IndicLegalQA",
            "status": "Database ready for searches"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
