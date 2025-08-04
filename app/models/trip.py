from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class TripStatus(str, Enum):
    """Trip status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"

class TripBase(BaseModel):
    """Base trip model"""
    schedule_id: str
    driver_id: str
    bus_id: str
    status: TripStatus = TripStatus.SCHEDULED
    actual_departure_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    current_location: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class TripCreate(TripBase):
    """Trip creation model"""
    pass

class TripResponse(TripBase):
    """Trip response model"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
