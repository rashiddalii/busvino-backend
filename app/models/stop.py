from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class StopBase(BaseModel):
    """Base stop model"""
    name: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = Field(None, max_length=500)

class StopCreate(StopBase):
    """Stop creation model"""
    pass

class StopResponse(StopBase):
    """Stop response model"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 