"""
Lawyer management routes for JurisLink.
Endpoints for lawyer profile creation, retrieval, and management.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from ..models.lawyer_model import LawyerCreate, LawyerUpdate, LawyerOut
from ..services.lawyer_service import LawyerService
from ..core.security import get_current_user


router = APIRouter(prefix="/lawyers", tags=["lawyers"])
lawyer_service = None


def get_lawyer_service():
    """Get or initialize lawyer service."""
    global lawyer_service
    if lawyer_service is None:
        lawyer_service = LawyerService()
    return lawyer_service


@router.post("", response_model=LawyerOut, status_code=status.HTTP_201_CREATED)
async def create_lawyer_profile(
    lawyer_data: LawyerCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a lawyer profile.
    Only users with role 'lawyer' can create their profile.
    """
    if current_user.get("role") != "lawyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can create lawyer profiles"
        )
    
    try:
        service = get_lawyer_service()
        lawyer = await service.create_lawyer(
            current_user["user_id"],
            current_user["email"],
            lawyer_data
        )
        return lawyer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{lawyer_id}", response_model=LawyerOut)
async def get_lawyer(lawyer_id: str):
    """Get lawyer profile by ID."""
    try:
        service = get_lawyer_service()
        lawyer = await service.get_lawyer_by_id(lawyer_id)
        if not lawyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lawyer not found"
            )
        return lawyer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=List[LawyerOut])
async def list_lawyers(
    skip: int = 0,
    limit: int = 50,
    specialization: Optional[str] = None,
    location: Optional[str] = None
):
    """
    List available lawyers.
    Can filter by specialization and location.
    """
    try:
        service = get_lawyer_service()
        
        if specialization or location:
            lawyers = await service.search_lawyers(
                specialization=specialization,
                location=location,
                skip=skip,
                limit=limit
            )
        else:
            lawyers = await service.get_all_lawyers(skip=skip, limit=limit)
        
        return lawyers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{lawyer_id}", response_model=LawyerOut)
async def update_lawyer_profile(
    lawyer_id: str,
    update_data: LawyerUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update lawyer profile. Only the lawyer can update their own profile."""
    try:
        service = get_lawyer_service()
        
        # Check if lawyer owns this profile
        lawyer = await service.get_lawyer_by_id(lawyer_id)
        if not lawyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lawyer not found"
            )
        
        if lawyer.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own lawyer profile"
            )
        
        updated = await service.update_lawyer(lawyer_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update lawyer profile"
            )
        
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
