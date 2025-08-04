from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, Field

class APIResponse(BaseModel):
    """Standard API response schema"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    errors: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat()) 