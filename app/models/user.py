from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class UserRole(str, Enum):
    """User role enumeration"""
    STUDENT = "student"
    EMPLOYEE = "employee"
    DRIVER = "driver"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    role: UserRole = UserRole.STUDENT
    status: UserStatus = UserStatus.ACTIVE
    organization_id: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)
    admin_id: Optional[str] = None  # ID of admin who created this user

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    organization_id: Optional[str] = None


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
    auth0_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None  # Admin who created the user

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

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

class UserFilter(BaseModel):
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    search: Optional[str] = None
    page: int = 1
    per_page: int = 20
