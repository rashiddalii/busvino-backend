from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field

class ScheduleBase(BaseModel):
    """Base schedule model"""
    route_id: str
    bus_id: str
    departure_time: time
    arrival_time: time
    days_of_week: list = Field(..., min_items=1, max_items=7)  # 1=Monday, 7=Sunday
    is_active: bool = True

class ScheduleCreate(ScheduleBase):
    """Schedule creation model"""
    pass

class ScheduleResponse(ScheduleBase):
    """Schedule response model"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
