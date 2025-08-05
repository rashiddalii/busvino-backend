from typing import List, Optional, Dict, Any
from app.config.database import get_supabase_client
from app.models.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserFilter, UserRole, UserStatus
from app.schemas.common import APIResponse
from app.core.auth import get_auth0_user
import requests
import json
from datetime import datetime

class UserService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.auth0_domain = "dev-f8dpug1be6jfleua.us.auth0.com"
        self.auth0_client_id = "HXAaWuTHXusGxNL2rgvJvmEdiYPxUWEm"
        self.auth0_client_secret = "your-auth0-client-secret"  # Set in environment

    async def create_user(self, user_data: UserCreate, admin_id: str) -> APIResponse:
        """Create a new user (admin only)"""
        try:
            # Create Auth0 user
            auth0_user = await self._create_auth0_user(user_data)
            
            # Save to Supabase
            supabase_user = await self._save_user_to_supabase(user_data, auth0_user["user_id"], admin_id)
            
            return APIResponse(
                success=True,
                message="User created successfully",
                data=supabase_user
            )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to create user",
                errors=[str(e)]
            )

    async def get_users(self, filters: UserFilter) -> APIResponse:
        """Get users with filtering and pagination (admin only)"""
        try:
            query = self.supabase.table("users").select("*")
            
            # Apply filters
            if filters.role:
                query = query.eq("role", filters.role.value)
            if filters.status:
                query = query.eq("status", filters.status.value)
            if filters.search:
                query = query.or_(f"name.ilike.%{filters.search}%,email.ilike.%{filters.search}%")
            
            # Apply pagination
            start = (filters.page - 1) * filters.per_page
            end = start + filters.per_page - 1
            query = query.range(start, end)
            
            # Get total count
            count_query = self.supabase.table("users").select("id", count="exact")
            if filters.role:
                count_query = count_query.eq("role", filters.role.value)
            if filters.status:
                count_query = count_query.eq("status", filters.status.value)
            if filters.search:
                count_query = count_query.or_(f"name.ilike.%{filters.search}%,email.ilike.%{filters.search}%")
            
            count_result = count_query.execute()
            total = count_result.count if hasattr(count_result, 'count') else 0
            
            # Get users
            result = query.execute()
            users = [UserResponse(**user) for user in result.data]
            
            return APIResponse(
                success=True,
                message="Users retrieved successfully",
                data=UserListResponse(
                    users=users,
                    total=total,
                    page=filters.page,
                    per_page=filters.per_page
                )
            )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to retrieve users",
                errors=[str(e)]
            )

    async def get_user(self, user_id: str) -> APIResponse:
        """Get a specific user by ID (admin only)"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not result.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            user = UserResponse(**result.data[0])
            return APIResponse(
                success=True,
                message="User retrieved successfully",
                data=user
            )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to retrieve user",
                errors=[str(e)]
            )

    async def update_user(self, user_id: str, user_data: UserUpdate) -> APIResponse:
        """Update a user (admin only)"""
        try:
            # Check if user exists
            existing_user = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if not existing_user.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            # Update in Supabase
            update_data = user_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                updated_user = UserResponse(**result.data[0])
                return APIResponse(
                    success=True,
                    message="User updated successfully",
                    data=updated_user
                )
            else:
                return APIResponse(
                    success=False,
                    message="Failed to update user",
                    errors=["Database update failed"]
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to update user",
                errors=[str(e)]
            )

    async def delete_user(self, user_id: str) -> APIResponse:
        """Delete a user (admin only)"""
        try:
            # Check if user exists
            existing_user = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if not existing_user.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            # Soft delete by setting status to inactive
            result = self.supabase.table("users").update({
                "status": UserStatus.INACTIVE.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if result.data:
                return APIResponse(
                    success=True,
                    message="User deleted successfully"
                )
            else:
                return APIResponse(
                    success=False,
                    message="Failed to delete user",
                    errors=["Database update failed"]
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to delete user",
                errors=[str(e)]
            )

    async def assign_role(self, user_id: str, role: UserRole) -> APIResponse:
        """Assign a role to a user (admin only)"""
        try:
            # Check if user exists
            existing_user = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if not existing_user.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            # Update role
            result = self.supabase.table("users").update({
                "role": role.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if result.data:
                updated_user = UserResponse(**result.data[0])
                return APIResponse(
                    success=True,
                    message=f"Role {role.value} assigned successfully",
                    data=updated_user
                )
            else:
                return APIResponse(
                    success=False,
                    message="Failed to assign role",
                    errors=["Database update failed"]
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to assign role",
                errors=[str(e)]
            )

    async def _create_auth0_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Create user in Auth0"""
        # Get Auth0 management token
        token_url = f"https://{self.auth0_domain}/oauth/token"
        token_payload = {
            "client_id": self.auth0_client_id,
            "client_secret": self.auth0_client_secret,
            "audience": f"https://{self.auth0_domain}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        token_response = requests.post(token_url, json=token_payload)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
        
        # Create Auth0 user
        user_url = f"https://{self.auth0_domain}/api/v2/users"
        user_payload = {
            "email": user_data.email,
            "password": user_data.password,
            "name": user_data.name,
            "connection": "Username-Password-Authentication",
            "email_verified": True
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.post(user_url, json=user_payload, headers=headers)
        user_response.raise_for_status()
        
        return user_response.json()

    async def _save_user_to_supabase(self, user_data: UserCreate, auth0_id: str, admin_id: str) -> Dict[str, Any]:
        """Save user to Supabase"""
        user_dict = {
            "auth0_id": auth0_id,
            "email": user_data.email,
            "name": user_data.name,
            "phone": user_data.phone,
            "location": user_data.location,
            "role": user_data.role.value,
            "status": user_data.status.value,
            "organization_id": user_data.organization_id,
            "created_by": admin_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table("users").insert(user_dict).execute()
        return result.data[0] if result.data else None 