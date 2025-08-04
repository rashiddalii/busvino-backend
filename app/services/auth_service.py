import os
import requests
from typing import Optional, Dict, Any
from jose import jwt
from app.config.settings import settings
from app.config.database import supabase_client
from app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, UserResponse
from app.schemas.common import APIResponse

class AuthService:
    """Authentication service for handling Auth0 and Supabase integration"""
    
    @staticmethod
    def get_management_token() -> str:
        """Get Auth0 management API token"""
        url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": f"https://{settings.AUTH0_DOMAIN}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["access_token"]
    
    @staticmethod
    def add_user_to_organization(org_id: str, user_id: str, mgmt_token: str) -> bool:
        """Add user to Auth0 organization"""
        url = f"https://{settings.AUTH0_DOMAIN}/api/v2/organizations/{org_id}/members"
        headers = {
            "Authorization": f"Bearer {mgmt_token}",
            "Content-Type": "application/json"
        }
        payload = {"members": [user_id]}
        
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 204
    
    @staticmethod
    def save_user_to_supabase(auth0_user_id: str, email: str, name: str, phone: str, location: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Save user to Supabase database"""
        user_data = {
            "auth0_id": auth0_user_id,
            "email": email,
            "name": name,
            "phone": phone,
            "location": location,
            "role": "student",
            "organization_id": org_id
        }
        
        result = supabase_client.table("users").insert(user_data).execute()
        return result.data[0] if result.data else {}
    
    @classmethod
    async def register_user(cls, payload: RegisterRequest) -> APIResponse:
        """Register a new user"""
        try:
            # Validate passwords match
            if payload.password != payload.confirm_password:
                return APIResponse(
                    success=False,
                    message="Registration failed",
                    errors=["Passwords do not match"]
                )
            
            # Get Auth0 management token
            token = cls.get_management_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Create user in Auth0
            auth0_data = {
                "email": payload.email,
                "password": payload.password,
                "connection": "Username-Password-Authentication"
            }
            
            response = requests.post(f"https://{settings.AUTH0_DOMAIN}/api/v2/users", json=auth0_data, headers=headers)
            if response.status_code != 201:
                error_detail = response.json()
                return APIResponse(
                    success=False,
                    message="Failed to create Auth0 user",
                    errors=[error_detail.get("message", "Unknown error")]
                )
            
            user_info = response.json()
            auth0_id = user_info["user_id"]
            email = user_info["email"]
            
            # Add to organization if specified
            auth0_org_id = None
            if payload.organization_id:
                try:
                    cls.add_user_to_organization(payload.organization_id, auth0_id, token)
                    auth0_org_id = payload.organization_id
                except Exception as e:
                    print(f"Warning: Failed to add user to organization: {e}")
            
            # Save user to Supabase
            supabase_user = cls.save_user_to_supabase(
                auth0_user_id=auth0_id,
                email=email,
                name=payload.name,
                phone=payload.phone,
                location=payload.location,
                org_id=auth0_org_id
            )
            
            # Return professional response
            return APIResponse(
                success=True,
                message="User registered successfully",
                data={
                    "user_id": supabase_user["id"],
                    "email": email,
                    "name": payload.name,
                    "role": "student",
                    "organization_id": auth0_org_id
                }
            )
            
        except Exception as e:
            return APIResponse(
                success=False,
                message="Registration failed",
                errors=[str(e)]
            )
    
    @classmethod
    async def login_user(cls, payload: LoginRequest) -> APIResponse:
        """Login user with Auth0"""
        try:
            # Auth0 login
            url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
            data = {
                "grant_type": "password",
                "username": payload.email,
                "password": payload.password,
                "audience": settings.API_AUDIENCE,
                "client_id": settings.AUTH0_CLIENT_ID,
                "client_secret": settings.AUTH0_CLIENT_SECRET,
                "scope": "openid email profile"
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                error_detail = response.json()
                return APIResponse(
                    success=False,
                    message="Login failed",
                    errors=[error_detail.get("error_description", "Invalid credentials")]
                )
            
            tokens = response.json()
            
            # Decode ID token to get Auth0 user ID
            id_token = tokens["id_token"]
            decoded_token = jwt.decode(
                id_token,
                key=None,
                options={"verify_signature": False, "verify_aud": False}
            )
            
            auth0_id = decoded_token["sub"]
            
            # Check Supabase
            supabase_result = supabase_client.table("users").select("*").eq("auth0_id", auth0_id).execute()
            if not supabase_result.data:
                return APIResponse(
                    success=False,
                    message="User not found",
                    errors=["User not found in system"]
                )
            
            user_data = supabase_result.data[0]
            
            # Return professional response
            return APIResponse(
                success=True,
                message="Login successful",
                data={
                    "access_token": tokens["access_token"],
                    "token_type": tokens["token_type"],
                    "expires_in": tokens["expires_in"],
                    "user": {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "name": user_data["name"],
                        "role": user_data["role"],
                        "organization_id": user_data.get("organization_id")
                    }
                }
            )
            
        except Exception as e:
            return APIResponse(
                success=False,
                message="Login failed",
                errors=[str(e)]
            ) 