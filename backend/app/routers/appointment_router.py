"""
Appointment router for JurisLink.
Handles appointment booking and management.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..models.appointment_model import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentOut
)
from ..core.security import get_current_user, require_role


router = APIRouter(prefix="/appointments", tags=["appointments"])
appointment_service = None


def get_appointment_service():
    """Lazy initialization of appointment service."""
    global appointment_service
    if appointment_service is None:
        from ..services.appointment_service import AppointmentService
        appointment_service = AppointmentService()
    return appointment_service


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_create: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Book a new appointment.
    
    Requests a time slot with a lawyer for a case.
    Automatically checks for lawyer's availability (no conflicts within duration).
    
    Args:
        appointment_create: Appointment data (case_id, lawyer_id, appointment_date, duration_minutes, notes)
        current_user: Authenticated user
        
    Returns:
        Created appointment with status 'scheduled'
        
    Raises:
        HTTPException: 400 if slot conflict, 401 if not authenticated, 500 on error
    """
    try:
        svc = get_appointment_service()
        appointment = await svc.create_appointment(
            appointment_create=appointment_create,
            user_id=current_user.get("user_id")
        )
        return appointment
    
    except Exception as e:
        if "conflicting" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment: {str(e)}"
        )


@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve an appointment by ID (involved parties/admin only).
    
    Args:
        appointment_id: Appointment identifier
        current_user: Authenticated user
        
    Returns:
        Appointment data
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not authorized, 404 if not found
    """
    svc = get_appointment_service()
    appointment = await svc.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")
    
    is_client = appointment.user_id == user_id
    is_lawyer = appointment.lawyer_id == user_id
    is_admin = user_role == "admin"
    
    if not (is_client or is_lawyer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this appointment"
        )
    
    return appointment


@router.get("/me", response_model=List[AppointmentOut])
async def get_my_appointments(
    current_user: dict = Depends(get_current_user)
):
    """
    List the current user's appointments.
    
    Returns appointments where the user is either the client or lawyer.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of user's appointments sorted by date
    """
    try:
        svc = get_appointment_service()
        appointments = await svc.get_user_appointments(
            user_id=current_user.get("user_id")
        )
        return appointments
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve appointments: {str(e)}"
        )


@router.patch("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    appointment_id: str,
    update_data: AppointmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an appointment (reschedule or change status).
    
    Client/Lawyer can update their own appointments.
    Admin can update any appointment.
    
    If rescheduling, automatically checks for conflicts.
    
    Args:
        appointment_id: Appointment to update
        update_data: Fields to update (slot_time, status, notes)
        current_user: Authenticated user
        
    Returns:
        Updated appointment
        
    Raises:
        HTTPException: 400 if conflict, 403 if not authorized, 404 if not found
    """
    svc = get_appointment_service()
    appointment = await svc.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")
    
    is_involved = (appointment.user_id == user_id or 
                   appointment.lawyer_id == user_id)
    is_admin = user_role == "admin"
    
    if not (is_involved or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    try:
        updated_appointment = await svc.update_appointment(
            appointment_id,
            update_data
        )
        
        if not updated_appointment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update appointment"
            )
        
        return updated_appointment
    
    except Exception as e:
        if "conflicting" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update appointment: {str(e)}"
        )


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
async def cancel_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an appointment.
    
    Client/Lawyer can cancel their own appointments.
    Admin can cancel any appointment.
    
    Args:
        appointment_id: Appointment to cancel
        current_user: Authenticated user
        
    Returns:
        Updated appointment with status 'cancelled'
        
    Raises:
        HTTPException: 403 if not authorized, 404 if not found
    """
    svc = get_appointment_service()
    appointment = await svc.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")
    
    is_involved = (appointment.user_id == user_id or 
                   appointment.lawyer_id == user_id)
    is_admin = user_role == "admin"
    
    if not (is_involved or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this appointment"
        )
    
    try:
        cancelled_appointment = await svc.cancel_appointment(
            appointment_id
        )
        
        if not cancelled_appointment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel appointment"
            )
        
        return cancelled_appointment
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel appointment: {str(e)}"
        )
