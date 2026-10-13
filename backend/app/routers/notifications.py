"""
Notification routes for JurisLink.
Endpoints for user notifications.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..models.notification_model import NotificationCreate, NotificationOut
from ..services.notification_service import NotificationService
from ..core.security import get_current_user


router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = None


def get_notification_service():
    global notification_service
    if notification_service is None:
        notification_service = NotificationService()
    return notification_service


@router.get("", response_model=List[NotificationOut])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get all notifications for current user."""
    try:
        service = get_notification_service()
        notifications = await service.get_user_notifications(
            current_user["user_id"],
            skip=skip,
            limit=limit
        )
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read."""
    try:
        service = get_notification_service()
        notification = await service.mark_as_read(notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return notification
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_read(
    current_user: dict = Depends(get_current_user)
):
    """Mark all notifications as read for current user."""
    try:
        service = get_notification_service()
        count = await service.mark_all_as_read(current_user["user_id"])
        return {"marked_read": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
