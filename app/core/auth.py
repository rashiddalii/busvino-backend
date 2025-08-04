import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config.settings import settings
from app.config.database import supabase_client
from app.models.user import UserRole, UserResponse, TokenData

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Auth0User class for compatibility
class Auth0User:
    def __init__(self, user_id: str, email: str, name: str, phone: str, location: str, role: str, organization_id: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.phone = phone
        self.location = location
        self.role = role
        self.organization_id = organization_id

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(user_id=user_id, email=email, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    token_data = verify_token(credentials.credentials)
    
    # Get user from Supabase
    result = supabase_client.table("users").select("*").eq("id", token_data.user_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = result.data[0]
    return UserResponse(**user_data)

async def require_role(required_role: UserRole):
    async def role_checker(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker

async def require_admin(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required"
        )
    return current_user

async def require_driver_or_admin(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role not in [UserRole.DRIVER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Driver or Admin role required"
        )
    return current_user

# Auth0 compatibility function
async def get_auth0_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Auth0User:
    """Get current user for Auth0 compatibility"""
    try:
        # Decode Auth0 token without verification (since we trust Auth0)
        token = credentials.credentials
        decoded_token = jwt.decode(
            token,
            key=None,
            options={"verify_signature": False, "verify_aud": False}
        )
        
        # Extract Auth0 user ID from token
        auth0_id = decoded_token["sub"]
        
        # Get user from Supabase using auth0_id
        result = supabase_client.table("users").select("*").eq("auth0_id", auth0_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = result.data[0]
        return Auth0User(
            user_id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            phone=user_data["phone"],
            location=user_data["location"],
            role=user_data["role"],
            organization_id=user_data.get("organization_id")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) 