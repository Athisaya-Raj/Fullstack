"""
Case router for JurisLink.
Handles case intake, retrieval, and status updates.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..models.case_model import CaseCreate, CaseStatusUpdate, CaseOut
from ..core.security import get_current_user, require_role


router = APIRouter(prefix="/cases", tags=["cases"])
case_service = None
classification_service = None


def get_services():
    """Lazy initialization of services."""
    global case_service, classification_service
    if case_service is None:
        from ..services.case_service import CaseService
        case_service = CaseService()
    if classification_service is None:
        from ..services.classification_service import ClassificationService
        classification_service = ClassificationService()
    return case_service, classification_service


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_create: CaseCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new legal case.
    
    Submits a legal issue. The issue text can be automatically:
    1. Classified into a category using NLP (when model ready)
    2. Summarized if documents provided (when model ready)
    
    Initial status is 'Submitted' until reviewed by admin.
    
    Args:
        case_create: Case creation data (title, description)
        current_user: Authenticated user
        
    Returns:
        Created case with ID and status
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    try:
        case_svc, classif_svc = get_services()
        
        # Create case (classification deferred until model ready)
        case = await case_svc.create_case(
            case_create=case_create,
            user_id=current_user.get("user_id")
        )
        
        return case
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )


@router.get("/{case_id}", response_model=CaseOut)
async def get_case(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a case by ID (owner/assigned lawyer/admin only).
    
    Args:
        case_id: Case identifier
        current_user: Authenticated user
        
    Returns:
        Case data
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not authorized, 404 if not found
    """
    case_svc, _ = get_services()
    case = await case_svc.get_case_by_id(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    is_owner = case.user_id == user_id
    is_assigned_lawyer = case.lawyer_id == user_id
    is_admin = user_role == "admin"
    
    if not (is_owner or is_assigned_lawyer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this case"
        )
    
    return case


@router.get("/me", response_model=List[CaseOut])
async def get_my_cases(
    current_user: dict = Depends(get_current_user)
):
    """
    List the logged-in user's cases.
    
    Filters based on user role:
    - User: returns their submitted cases
    - Lawyer: returns cases assigned to them
    - Admin: returns all cases
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of relevant cases
    """
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    case_svc, _ = get_services()
    
    try:
        if user_role == "lawyer":
            cases = await case_svc.get_cases_assigned_to_lawyer(user_id)
        else:
            cases = await case_svc.get_user_cases(user_id)
        
        return cases
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cases: {str(e)}"
        )


@router.get("/lawyer/{lawyer_id}", response_model=List[CaseOut])
async def get_lawyer_cases(
    lawyer_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Get cases assigned to a lawyer (admin only).
    
    Args:
        lawyer_id: Lawyer identifier
        current_user: Admin user
        
    Returns:
        List of cases assigned to lawyer
    """
    try:
        case_svc, _ = get_services()
        cases = await case_svc.get_cases_assigned_to_lawyer(lawyer_id)
        return cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve lawyer cases: {str(e)}"
        )


@router.patch("/{case_id}/status", response_model=CaseOut)
async def update_case_status(
    case_id: str,
    status_update: CaseStatusUpdate,
    current_user: dict = Depends(require_role("lawyer", "admin"))
):
    """
    Update a case's status (lawyer/admin only).
    
    Allowed transitions:
    - Submitted → Under Review → Assigned → In Progress → Resolved
    
    Args:
        case_id: Case to update
        status_update: New status value
        current_user: Lawyer or admin user
        
    Returns:
        Updated case
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not lawyer/admin, 404 if not found
    """
    case_svc, _ = get_services()
    case = await case_svc.get_case_by_id(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization: assigned lawyer or admin
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")
    
    is_assigned_lawyer = case.lawyer_id == user_id
    is_admin = user_role == "admin"
    
    if not (is_assigned_lawyer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this case"
        )
    
    try:
        updated_case = await case_svc.update_case_status(case_id, status_update)
        
        if not updated_case:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update case status"
            )
        
        return updated_case
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update case: {str(e)}"
        )


@router.post("/{case_id}/assign", response_model=CaseOut)
async def assign_case_to_lawyer(
    case_id: str,
    lawyer_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Assign a case to a lawyer (admin only).
    
    Sets case status to 'assigned' and links the lawyer.
    
    Args:
        case_id: Case to assign
        lawyer_id: Lawyer to assign to
        current_user: Admin user
        
    Returns:
        Updated case with assigned lawyer
    """
    try:
        case_svc, _ = get_services()
        assigned_case = await case_svc.assign_case_to_lawyer(case_id, lawyer_id)
        
        if not assigned_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        return assigned_case
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign case: {str(e)}"
        )
