from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.user import UserCreate, UserUpdate, UserFilter, UserRole, UserStatus
from app.services.user_service import UserService
from app.core.auth import get_auth0_user, require_admin, Auth0User
from app.schemas.common import APIResponse
from app.schemas.auth import UserResponse

router = APIRouter()

# User-side CRUD operations (scoped to authenticated user)
@router.get("/me", response_model=APIResponse)
async def get_my_profile(
    current_user: Auth0User = Depends(get_auth0_user),
    user_service: UserService = Depends()
):
    """Get current user's profile"""
    result = await user_service.get_my_profile(current_user.user_id)
    
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    
    return result

@router.put("/me", response_model=APIResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: Auth0User = Depends(get_auth0_user),
    user_service: UserService = Depends()
):
    """Update current user's profile"""
    result = await user_service.update_my_profile(current_user.user_id, user_data)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.delete("/me", response_model=APIResponse)
async def delete_my_account(
    current_user: Auth0User = Depends(get_auth0_user),
    user_service: UserService = Depends()
):
    """Delete current user's account"""
    result = await user_service.delete_my_account(current_user.user_id)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

# Admin-side CRUD operations (admin only)
@router.post("/", response_model=APIResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Auth0User = Depends(require_admin),
    user_service: UserService = Depends()
):
    """Create a new user (Admin only)"""
    result = await user_service.create_user(user_data, current_user.user_id)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.get("/", response_model=APIResponse)
async def get_users(
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Auth0User = Depends(require_admin),
    user_service: UserService = Depends()
):
    """Get all users with filtering and pagination (Admin only)"""
    filters = UserFilter(
        role=role,
        status=status,
        search=search,
        page=page,
        per_page=per_page
    )
    
    result = await user_service.get_users(filters)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.get("/{user_id}", response_model=APIResponse)
async def get_user(
    user_id: str,
    current_user: Auth0User = Depends(require_admin),
    user_service: UserService = Depends()
):
    """Get a specific user by ID (Admin only)"""
    result = await user_service.get_user(user_id)
    
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    
    return result

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Auth0User = Depends(require_admin),
    user_service: UserService = Depends()
):
    """Update a user (Admin only)"""
    result = await user_service.update_user(user_id, user_data)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: str,
    current_user: Auth0User = Depends(require_admin),
    user_service: UserService = Depends()
):
    """Delete a user (Admin only)"""
    result = await user_service.delete_user(user_id)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.patch("/{user_id}/role", response_model=APIResponse)
async def assign_role(
    user_id: str,
    role: UserRole,
    current_user: Auth0User = Depends(require_admin),
    user_service: UserService = Depends()
):
    """Assign a role to a user (Admin only)"""
    result = await user_service.assign_role(user_id, role)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.get("/roles/available", response_model=APIResponse)
async def get_available_roles(
    current_user: Auth0User = Depends(require_admin)
):
    """Get available user roles (Admin only)"""
    roles = [
        {"value": role.value, "label": role.value.title()} 
        for role in UserRole
    ]
    
    return APIResponse(
        success=True,
        message="Available roles retrieved successfully",
        data={"roles": roles}
    )

@router.get("/statuses/available", response_model=APIResponse)
async def get_available_statuses(
    current_user: Auth0User = Depends(require_admin)
):
    """Get available user statuses (Admin only)"""
    statuses = [
        {"value": status.value, "label": status.value.title()} 
        for status in UserStatus
    ]
    
    return APIResponse(
        success=True,
        message="Available statuses retrieved successfully",
        data={"statuses": statuses}
    ) 