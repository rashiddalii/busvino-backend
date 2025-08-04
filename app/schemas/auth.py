from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=1)

class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    location: str = Field(..., min_length=1, max_length=200)
    organization_id: Optional[str] = None

class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    name: str
    role: str
    organization_id: Optional[str] = None

class AuthResponse(BaseModel):
    """Authentication response schema"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse 