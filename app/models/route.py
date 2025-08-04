from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class RouteBase(BaseModel):
    """Base route model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_location: str = Field(..., min_length=1, max_length=200)
    end_location: str = Field(..., min_length=1, max_length=200)
    estimated_duration: int = Field(..., gt=0)  # in minutes
    distance: float = Field(..., gt=0)  # in kilometers

class RouteCreate(RouteBase):
    """Route creation model"""
    pass

class RouteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RouteResponse(RouteBase):
    """Route response model"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
