"""
Legal search routes for JurisLink.
Endpoints for searching and retrieving public legal knowledge.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from ..models.legal_case_model import LegalCaseOut, LegalCaseSearch
from ..services.legal_case_service import LegalCaseService


router = APIRouter(prefix="/legal", tags=["legal-search"])
legal_case_service = None


def get_legal_case_service():
    global legal_case_service
    if legal_case_service is None:
        legal_case_service = LegalCaseService()
    return legal_case_service


@router.get("/search", response_model=List[LegalCaseOut])
async def search_legal_cases(
    query: Optional[str] = Query(None, description="Search query"),
    legal_category: Optional[str] = None,
    case_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    """Search legal cases from Supreme Court database."""
    try:
        service = get_legal_case_service()
        
        search_params = LegalCaseSearch(
            query=query,
            legal_category=legal_category,
            case_type=case_type,
            skip=skip,
            limit=limit
        )
        
        cases = await service.search_legal_cases(search_params)
        return cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/cases/{case_id}", response_model=LegalCaseOut)
async def get_legal_case(case_id: str):
    """Get a specific legal case."""
    try:
        service = get_legal_case_service()
        case = await service.get_legal_case_by_id(case_id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal case not found"
            )
        
        return case
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/categories/{category}", response_model=List[LegalCaseOut])
async def get_cases_by_category(
    category: str,
    skip: int = 0,
    limit: int = 50
):
    """Get legal cases by legal category."""
    try:
        service = get_legal_case_service()
        cases = await service.get_cases_by_category(
            category=category,
            skip=skip,
            limit=limit
        )
        return cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_legal_database_stats():
    """Get statistics about the legal case database."""
    try:
        service = get_legal_case_service()
        total_cases = await service.get_total_count()
        
        return {
            "total_legal_cases": total_cases,
            "source": "Supreme Court of India",
            "status": "Database ready for searches"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
