"""
Notification Service for JurisLink.
Handles user notifications for case updates, appointments, etc.
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from ..models.notification_model import NotificationCreate, NotificationOut
from ..db.mongodb import get_database


class NotificationService:
    """Service for managing user notifications."""
    
    def __init__(self):
        self.db = None
        self.collection_name = "notifications"
    
    def _get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> NotificationOut:
        """Create a new notification."""
        db = self._get_db()
        
        notification_doc = {
            "user_id": ObjectId(notification_data.user_id),
            "case_id": ObjectId(notification_data.case_id) if notification_data.case_id else None,
            "type": notification_data.notification_type.value,
            "title": notification_data.title,
            "message": notification_data.message,
            "read": False,
            "created_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(notification_doc)
        notification_doc["_id"] = result.inserted_id
        
        return self._format_notification_out(notification_doc)
    
    async def get_user_notifications(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[NotificationOut]:
        """Get all notifications for a user."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        notifications = []
        async for notification in cursor:
            notifications.append(self._format_notification_out(notification))
        
        return notifications
    
    async def mark_as_read(self, notification_id: str) -> Optional[NotificationOut]:
        """Mark a notification as read."""
        try:
            db = self._get_db()
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(notification_id)},
                {"$set": {"read": True}},
                return_document=True
            )
            
            if result:
                return self._format_notification_out(result)
            return None
        except Exception:
            return None
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        try:
            db = self._get_db()
            result = await db[self.collection_name].update_many(
                {"user_id": ObjectId(user_id), "read": False},
                {"$set": {"read": True}}
            )
            return result.modified_count
        except Exception:
            return 0
    
    def _format_notification_out(self, notification_doc: dict) -> NotificationOut:
        """Convert MongoDB notification to NotificationOut."""
        return NotificationOut(
            notification_id=str(notification_doc["_id"]),
            user_id=str(notification_doc["user_id"]),
            case_id=str(notification_doc["case_id"]) if notification_doc.get("case_id") else None,
            notification_type=notification_doc["type"],
            title=notification_doc["title"],
            message=notification_doc["message"],
            read=notification_doc.get("read", False),
            created_at=notification_doc["created_at"],
        )
