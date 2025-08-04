from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.core.auth import get_auth0_user

router = APIRouter()

@router.post("/register", response_model=APIResponse)
async def register(payload: RegisterRequest):
    """Register a new user"""
    return await AuthService.register_user(payload)

@router.post("/login", response_model=APIResponse)
async def login(payload: LoginRequest):
    """Login user"""
    return await AuthService.login_user(payload)

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_auth0_user)):
    """Get current user information"""
    return {
        "message": "Access granted",
        "user": {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.name,
            "phone": current_user.phone,
            "location": current_user.location,
            "role": current_user.role,
            "organization_id": current_user.organization_id
        }
    }

@router.get("/protected")
async def protected_route(current_user = Depends(get_auth0_user)):
    """Protected route example"""
    return {
        "message": "Access granted",
        "user": {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.name,
            "phone": current_user.phone,
            "location": current_user.location,
            "role": current_user.role,
            "organization_id": current_user.organization_id
        }
    } 