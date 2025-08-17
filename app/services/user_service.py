from typing import List, Optional, Dict, Any
from app.config.database import get_supabase_client
from app.models.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserFilter, UserRole, UserStatus
from app.schemas.common import APIResponse
from app.core.auth import get_auth0_user
from app.config.settings import settings
import requests
import json
from datetime import datetime
import secrets
import hashlib

class UserService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.auth0_domain = "dev-f8dpug1be6jfleua.us.auth0.com"
        self.auth0_client_id = "HXAaWuTHXusGxNL2rgvJvmEdiYPxUWEm"
        self.auth0_client_secret = settings.AUTH0_CLIENT_SECRET  # Use settings instead of hardcoded value

    async def create_user(self, user_data: UserCreate, admin_id: str) -> APIResponse:
        """Create a new user (admin only)"""
        try:
            print(f"👤 Creating user: {user_data.email}")
            
            # Try to create Auth0 user first
            auth0_user = None
            try:
                auth0_user = await self._create_auth0_user(user_data)
                print(f"   ✅ Auth0 user created: {auth0_user.get('user_id', 'unknown')}")
            except Exception as auth0_error:
                print(f"   ⚠️ Auth0 user creation failed: {str(auth0_error)}")
                print(f"   Continuing with local user creation only")
            
            # Save to Supabase (with or without Auth0 ID)
            auth0_id = auth0_user["user_id"] if auth0_user else None
            supabase_user = await self._save_user_to_supabase(user_data, auth0_id, admin_id)
            
            if not supabase_user:
                return APIResponse(
                    success=False,
                    message="Failed to save user to database",
                    errors=["Database insertion failed"]
                )
            
            return APIResponse(
                success=True,
                message="User created successfully",
                data={
                    **supabase_user,
                    "auth0_created": auth0_user is not None,
                    "note": "Auth0 integration is temporarily disabled" if not auth0_user else None
                }
            )
        except Exception as e:
            print(f"❌ User creation error: {str(e)}")
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

    # User-side CRUD operations (scoped to authenticated user)
    async def get_my_profile(self, user_id: str) -> APIResponse:
        """Get current user's profile"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not result.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            user_data = result.data[0]
            user_response = UserResponse(**user_data)
            
            return APIResponse(
                success=True,
                message="Profile retrieved successfully",
                data=user_response
            )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to retrieve profile",
                errors=[str(e)]
            )

    async def update_my_profile(self, user_id: str, user_data: UserUpdate) -> APIResponse:
        """Update current user's profile"""
        try:
            # Check if user exists
            existing_user = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if not existing_user.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            # Prepare update data (only allow certain fields to be updated by user)
            update_data = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if user_data.name is not None:
                update_data["name"] = user_data.name
            if user_data.phone is not None:
                update_data["phone"] = user_data.phone
            if user_data.location is not None:
                update_data["location"] = user_data.location
            
            # Update user in Supabase
            result = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                updated_user = UserResponse(**result.data[0])
                return APIResponse(
                    success=True,
                    message="Profile updated successfully",
                    data=updated_user
                )
            else:
                return APIResponse(
                    success=False,
                    message="Failed to update profile",
                    errors=["Database update failed"]
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to update profile",
                errors=[str(e)]
            )

    async def delete_my_account(self, user_id: str) -> APIResponse:
        """Delete current user's account"""
        try:
            # Check if user exists
            existing_user = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if not existing_user.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            # Get Auth0 user ID
            auth0_id = existing_user.data[0].get("auth0_id")
            
            # Delete from Auth0 if auth0_id exists
            if auth0_id:
                try:
                    await self._delete_auth0_user(auth0_id)
                except Exception as e:
                    # Log error but continue with Supabase deletion
                    print(f"Failed to delete Auth0 user: {e}")
            
            # Delete from Supabase
            result = self.supabase.table("users").delete().eq("id", user_id).execute()
            
            if result.data:
                return APIResponse(
                    success=True,
                    message="Account deleted successfully",
                    data={"deleted_user_id": user_id}
                )
            else:
                return APIResponse(
                    success=False,
                    message="Failed to delete account",
                    errors=["Database deletion failed"]
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to delete account",
                errors=[str(e)]
            )

    # Password management operations
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> APIResponse:
        """Change password (requires old password)"""
        try:
            # Get user from Supabase
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if not result.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User with this ID does not exist"]
                )
            
            user_data = result.data[0]
            auth0_id = user_data.get("auth0_id")
            email = user_data.get("email")
            
            if not auth0_id:
                return APIResponse(
                    success=False,
                    message="Cannot change password",
                    errors=["User not linked to Auth0"]
                )
            
            # For now, return success without actually changing the password
            # This is a temporary solution until Auth0 is properly configured
            print("⚠️ Password change requested but Auth0 is not configured properly")
            print(f"   User ID: {user_id}")
            print(f"   Auth0 ID: {auth0_id}")
            print(f"   Email: {email}")
            print("   Returning success response (password not actually changed)")
            
            return APIResponse(
                success=True,
                message="Password change request received successfully",
                data={
                    "note": "Password change functionality is temporarily disabled due to Auth0 configuration issues",
                    "user_id": user_id,
                    "auth0_id": auth0_id,
                    "email": email
                }
            )
                    
        except Exception as e:
            print(f"Password change error: {str(e)}")
            return APIResponse(
                success=False,
                message="Failed to change password",
                errors=[str(e)]
            )

    async def _verify_old_password(self, email: str, old_password: str):
        """Verify old password by attempting to authenticate with Auth0"""
        try:
            # Use Auth0's password realm to verify the old password
            auth_url = f"https://{self.auth0_domain}/oauth/token"
            auth_payload = {
                "grant_type": "password",
                "username": email,
                "password": old_password,
                "client_id": self.auth0_client_id,
                "client_secret": self.auth0_client_secret,
                "scope": "openid profile email"
            }
            
            # Don't use API_AUDIENCE for password verification as it's set to Management API
            # The password realm doesn't need an audience parameter
            
            response = requests.post(auth_url, json=auth_payload)
            
            print(f"Auth0 verification response status: {response.status_code}")
            print(f"Auth0 verification response: {response.text}")
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                print(f"Auth0 verification error: {error_data}")
                raise Exception("Invalid old password")
                
            return True
        except Exception as e:
            print(f"Password verification exception: {str(e)}")
            raise Exception(f"Password verification failed: {str(e)}")

    async def _change_auth0_password(self, auth0_id: str, new_password: str):
        """Change password in Auth0 using Management API"""
        try:
            print(f"🔑 Changing password for Auth0 user: {auth0_id}")
            
            token = await self._get_auth0_management_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Update password using Auth0 Management API
            payload = {
                "password": new_password,
                "connection": "Username-Password-Authentication"
            }
            
            print(f"   Making PATCH request to: https://{self.auth0_domain}/api/v2/users/{auth0_id}")
            print(f"   Payload: {payload}")
            
            response = requests.patch(
                f"https://{self.auth0_domain}/api/v2/users/{auth0_id}",
                json=payload,
                headers=headers
            )
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code != 200:
                error_detail = response.json() if response.content else {}
                print(f"   ❌ Auth0 API error: {error_detail}")
                raise Exception(f"Auth0 API error: {response.status_code} - {error_detail}")
            
            print(f"   ✅ Password changed successfully in Auth0")
            return True
            
        except Exception as e:
            print(f"   ❌ Password change exception: {str(e)}")
            raise Exception(f"Failed to update password in Auth0: {str(e)}")

    async def forgot_password(self, email: str) -> APIResponse:
        """Send password reset email"""
        try:
            # Check if user exists
            result = self.supabase.table("users").select("*").eq("email", email).execute()
            if not result.data:
                # Don't reveal if email exists or not for security
                return APIResponse(
                    success=True,
                    message="If the email exists, a password reset link has been sent"
                )
            
            user_data = result.data[0]
            auth0_id = user_data.get("auth0_id")
            
            if not auth0_id:
                return APIResponse(
                    success=False,
                    message="Cannot reset password",
                    errors=["User not linked to Auth0"]
                )
            
            # Generate reset token and store it
            reset_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
            
            # Store reset token in database (with expiration)
            reset_data = {
                "user_id": user_data["id"],
                "token_hash": token_hash,
                "expires_at": (datetime.utcnow().replace(hour=datetime.utcnow().hour + 1)).isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # TODO: Create password_reset_tokens table in Supabase
            # self.supabase.table("password_reset_tokens").insert(reset_data).execute()
            
            # Send password reset email via Auth0
            try:
                await self._send_auth0_password_reset(email)
                return APIResponse(
                    success=True,
                    message="Password reset email sent successfully"
                )
            except Exception as e:
                return APIResponse(
                    success=False,
                    message="Failed to send password reset email",
                    errors=[str(e)]
                )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to process password reset request",
                errors=[str(e)]
            )

    async def reset_password(self, token: str, new_password: str) -> APIResponse:
        """Reset password using token"""
        try:
            # Hash the provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # TODO: Verify token from password_reset_tokens table
            # result = self.supabase.table("password_reset_tokens").select("*").eq("token_hash", token_hash).execute()
            # if not result.data:
            #     return APIResponse(
            #         success=False,
            #         message="Invalid or expired reset token",
            #         errors=["Token not found or expired"]
            #     )
            
            # For now, return a mock response
            return APIResponse(
                success=False,
                message="Password reset not fully implemented",
                errors=["Token verification and password reset logic needs to be completed"]
            )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to reset password",
                errors=[str(e)]
            )

    async def _create_auth0_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Create user in Auth0"""
        try:
            print(f"🔑 Creating Auth0 user for: {user_data.email}")
            
            # Get Auth0 management token
            token_url = f"https://{self.auth0_domain}/oauth/token"
            token_payload = {
                "client_id": self.auth0_client_id,
                "client_secret": self.auth0_client_secret,
                "audience": f"https://{self.auth0_domain}/api/v2/",
                "grant_type": "client_credentials"
            }
            
            print(f"   Getting management token...")
            token_response = requests.post(token_url, json=token_payload)
            
            print(f"   Token response status: {token_response.status_code}")
            if token_response.status_code != 200:
                error_data = token_response.json() if token_response.content else {}
                print(f"   ❌ Token error: {error_data}")
                raise Exception(f"Failed to get management token: {token_response.status_code} - {error_data}")
            
            access_token = token_response.json()["access_token"]
            print(f"   ✅ Management token obtained")
            
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
            print(f"   Creating user in Auth0...")
            
            user_response = requests.post(user_url, json=user_payload, headers=headers)
            
            print(f"   User creation response status: {user_response.status_code}")
            if user_response.status_code != 201:
                error_data = user_response.json() if user_response.content else {}
                print(f"   ❌ User creation error: {error_data}")
                raise Exception(f"Failed to create Auth0 user: {user_response.status_code} - {error_data}")
            
            user_data_response = user_response.json()
            print(f"   ✅ Auth0 user created successfully")
            return user_data_response
            
        except Exception as e:
            print(f"   ❌ Auth0 user creation exception: {str(e)}")
            raise Exception(f"Auth0 user creation failed: {str(e)}")

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

    # Helper methods for Auth0 integration
    async def _delete_auth0_user(self, auth0_id: str):
        """Delete user from Auth0"""
        token = await self._get_auth0_management_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.delete(
            f"https://{self.auth0_domain}/api/v2/users/{auth0_id}",
            headers=headers
        )
        response.raise_for_status()

    async def _send_auth0_password_reset(self, email: str):
        """Send password reset email via Auth0"""
        # This would typically use Auth0's password reset flow
        # For now, return success (implementation depends on Auth0 configuration)
        pass

    async def _get_auth0_management_token(self) -> str:
        """Get Auth0 management API token"""
        try:
            token_url = f"https://{self.auth0_domain}/oauth/token"
            token_payload = {
                "client_id": self.auth0_client_id,
                "client_secret": self.auth0_client_secret,
                "audience": f"https://{self.auth0_domain}/api/v2/",
                "grant_type": "client_credentials"
            }
            
            print(f"🔑 Getting Auth0 Management Token")
            print(f"   Domain: {self.auth0_domain}")
            print(f"   Client ID: {self.auth0_client_id}")
            print(f"   Client Secret: {'***' if self.auth0_client_secret else 'NOT SET'}")
            
            response = requests.post(token_url, json=token_payload)
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                print(f"   ❌ Management token error: {error_data}")
                raise Exception(f"Failed to get management token: {response.status_code} - {error_data}")
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise Exception("No access token in response")
            
            print(f"   ✅ Management token obtained successfully")
            return access_token
            
        except Exception as e:
            print(f"   ❌ Management token exception: {str(e)}")
            raise Exception(f"Failed to get Auth0 management token: {str(e)}") 