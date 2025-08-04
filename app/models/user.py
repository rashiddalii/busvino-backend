from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class UserRole(str, Enum):
    """User role enumeration"""
    STUDENT = "student"
    EMPLOYEE = "employee"
    DRIVER = "driver"
    ADMIN = "admin"

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    location: str = Field(..., min_length=1, max_length=200)
    role: UserRole = UserRole.STUDENT
    organization_id: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserFavoriteRouteBase(BaseModel):
    user_id: str
    route_id: str

class UserFavoriteRouteCreate(UserFavoriteRouteBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class UserResponse(UserBase):
    """User response model"""
    id: str
    auth0_id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserDashboard(BaseModel):
    user: UserResponse
    favorite_routes: list  # List[RouteResponse]
    upcoming_schedules: list  # List[ScheduleResponse]
    recent_announcements: list  # List[AnnouncementResponse]

class RouteDetails(BaseModel):
    route: object  # RouteResponse
    stops: list  # List[RouteStopResponse]
    schedules: list  # List[ScheduleResponse]
    current_trips: list  # List[TripResponse]

class TokenData(BaseModel):
    """Token data model"""
    user_id: str
    email: str
    role: str
