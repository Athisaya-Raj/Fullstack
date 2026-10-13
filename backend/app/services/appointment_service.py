"""
Appointment Service for JurisLink.
Handles appointment scheduling, rescheduling, and conflict detection.
"""
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from ..models.appointment_model import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentOut,
    AppointmentStatus
)
from ..db.mongodb import get_database


class AppointmentService:
    """Service for managing appointments."""
    
    def __init__(self):
        """Initialize appointment service."""
        self.db = None
        self.collection_name = "appointments"
    
    def _get_db(self):
        """Get database, lazy loading."""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def create_appointment(
        self,
        user_id: str,
        appointment_data: AppointmentCreate
    ) -> AppointmentOut:
        """Create a new appointment."""
        db = self._get_db()
        
        # Check for conflicts
        conflict = await self._check_lawyer_conflict(
            appointment_data.lawyer_id,
            appointment_data.appointment_date,
            appointment_data.duration_minutes
        )
        
        if conflict:
            raise Exception(
                f"Lawyer has conflicting appointment. Available time slots must not overlap."
            )
        
        appointment_doc = {
            "case_id": ObjectId(appointment_data.case_id),
            "user_id": ObjectId(user_id),
            "lawyer_id": ObjectId(appointment_data.lawyer_id),
            "appointment_date": appointment_data.appointment_date,
            "duration_minutes": appointment_data.duration_minutes,
            "status": AppointmentStatus.SCHEDULED.value,
            "notes": appointment_data.notes,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        result = await db[self.collection_name].insert_one(appointment_doc)
        appointment_doc["_id"] = result.inserted_id
        
        return self._format_appointment_out(appointment_doc)
    
    async def get_appointment_by_id(self, appointment_id: str) -> Optional[AppointmentOut]:
        """Retrieve an appointment by ID."""
        try:
            db = self._get_db()
            appointment = await db[self.collection_name].find_one(
                {"_id": ObjectId(appointment_id)}
            )
            if appointment:
                return self._format_appointment_out(appointment)
            return None
        except Exception:
            return None
    
    async def get_user_appointments(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[AppointmentOut]:
        """Get appointments for a user."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"user_id": ObjectId(user_id)}
        ).sort("appointment_date", 1).skip(skip).limit(limit)
        
        appointments = []
        async for appointment in cursor:
            appointments.append(self._format_appointment_out(appointment))
        
        return appointments
    
    async def get_lawyer_appointments(
        self,
        lawyer_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[AppointmentOut]:
        """Get appointments for a lawyer."""
        db = self._get_db()
        cursor = db[self.collection_name].find(
            {"lawyer_id": ObjectId(lawyer_id)}
        ).sort("appointment_date", 1).skip(skip).limit(limit)
        
        appointments = []
        async for appointment in cursor:
            appointments.append(self._format_appointment_out(appointment))
        
        return appointments
    
    async def update_appointment(
        self,
        appointment_id: str,
        update_data: AppointmentUpdate
    ) -> Optional[AppointmentOut]:
        """Update an appointment."""
        try:
            db = self._get_db()
            
            # Get existing appointment
            existing = await db[self.collection_name].find_one(
                {"_id": ObjectId(appointment_id)}
            )
            
            if not existing:
                return None
            
            # Check for conflict if rescheduling
            if update_data.appointment_date:
                duration = update_data.duration_minutes or existing.get("duration_minutes", 30)
                conflict = await self._check_lawyer_conflict(
                    str(existing["lawyer_id"]),
                    update_data.appointment_date,
                    duration,
                    exclude_appointment_id=appointment_id
                )
                
                if conflict:
                    raise Exception("Time slot conflict with another appointment")
            
            # Build update dict
            update_dict = {"updated_at": datetime.now(timezone.utc)}
            
            if update_data.appointment_date is not None:
                update_dict["appointment_date"] = update_data.appointment_date
            if update_data.duration_minutes is not None:
                update_dict["duration_minutes"] = update_data.duration_minutes
            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            if update_data.notes is not None:
                update_dict["notes"] = update_data.notes
            
            # Update in database
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(appointment_id)},
                {"$set": update_dict},
                return_document=True
            )
            
            if result:
                return self._format_appointment_out(result)
            return None
        except Exception as e:
            if "conflict" in str(e).lower():
                raise
            return None
    
    async def cancel_appointment(self, appointment_id: str) -> Optional[AppointmentOut]:
        """Cancel an appointment."""
        try:
            db = self._get_db()
            result = await db[self.collection_name].find_one_and_update(
                {"_id": ObjectId(appointment_id)},
                {
                    "$set": {
                        "status": AppointmentStatus.CANCELLED.value,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                return_document=True
            )
            
            if result:
                return self._format_appointment_out(result)
            return None
        except Exception:
            return None
    
    async def _check_lawyer_conflict(
        self,
        lawyer_id: str,
        appointment_date: datetime,
        duration_minutes: int,
        exclude_appointment_id: Optional[str] = None
    ) -> bool:
        """Check if lawyer has conflicting appointments."""
        db = self._get_db()
        
        # Calculate end time
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        # Find overlapping appointments
        query = {
            "lawyer_id": ObjectId(lawyer_id),
            "status": AppointmentStatus.SCHEDULED.value,
            "$or": [
                {
                    "appointment_date": {
                        "$lt": end_time,
                        "$gte": appointment_date
                    }
                },
                {
                    "$expr": {
                        "$lt": [
                            {"$add": ["$appointment_date", {"$multiply": ["$duration_minutes", 60000]}]},
                            appointment_date
                        ]
                    }
                }
            ]
        }
        
        if exclude_appointment_id:
            try:
                query["_id"] = {"$ne": ObjectId(exclude_appointment_id)}
            except Exception:
                pass
        
        conflict = await db[self.collection_name].find_one(query)
        return conflict is not None
    
    def _format_appointment_out(self, appointment_doc: dict) -> AppointmentOut:
        """Convert MongoDB appointment to AppointmentOut."""
        return AppointmentOut(
            appointment_id=str(appointment_doc["_id"]),
            case_id=str(appointment_doc["case_id"]),
            user_id=str(appointment_doc["user_id"]),
            lawyer_id=str(appointment_doc["lawyer_id"]),
            appointment_date=appointment_doc["appointment_date"],
            duration_minutes=appointment_doc.get("duration_minutes", 30),
            status=appointment_doc["status"],
            notes=appointment_doc.get("notes"),
            created_at=appointment_doc.get("created_at"),
            updated_at=appointment_doc.get("updated_at"),
        )
