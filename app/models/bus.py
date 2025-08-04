from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class BusStatus(str, Enum):
    """Bus status enumeration"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class BusBase(BaseModel):
    """Base bus model"""
    license_plate: str = Field(..., min_length=5, max_length=20)
    capacity: int = Field(..., gt=0, le=100)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1990, le=2030)
    status: BusStatus = BusStatus.ACTIVE
    driver_id: Optional[str] = None

class BusCreate(BusBase):
    """Bus creation model"""
    pass

class BusResponse(BusBase):
    """Bus response model"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
