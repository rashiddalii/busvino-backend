from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BusLocationBase(BaseModel):
    bus_id: str
    trip_id: str
    latitude: float
    longitude: float
    speed: Optional[float] = None
    heading: Optional[float] = None

class BusLocationCreate(BusLocationBase):
    pass

class BusLocationResponse(BusLocationBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True
