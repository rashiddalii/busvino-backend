from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.auth import get_auth0_user, Auth0User

router = APIRouter()

@router.post("/register", response_model=APIResponse)
async def register(payload: RegisterRequest):
    """Register a new user"""
    return await AuthService.register_user(payload)

@router.post("/login", response_model=APIResponse)
async def login(payload: LoginRequest):
    """Login user"""
    return await AuthService.login_user(payload)

@router.post("/change-password", response_model=APIResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Auth0User = Depends(get_auth0_user),
    user_service: UserService = Depends()
):
    """Change password (requires old password)"""
    # TODO: Add rate limiting to prevent brute force attacks
    
    # Validate password confirmation
    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(
            status_code=400, 
            detail="New password and confirmation password do not match"
        )
    
    result = await user_service.change_password(
        current_user.user_id, 
        payload.old_password, 
        payload.new_password
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    user_service: UserService = Depends()
):
    """Request password reset (email-based)"""
    # TODO: Add rate limiting to prevent email spam
    result = await user_service.forgot_password(payload.email)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.post("/reset-password", response_model=APIResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    user_service: UserService = Depends()
):
    """Reset password with token"""
    # TODO: Add rate limiting to prevent brute force attacks
    
    # Validate password confirmation
    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(
            status_code=400, 
            detail="New password and confirmation password do not match"
        )
    
    result = await user_service.reset_password(payload.token, payload.new_password)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

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