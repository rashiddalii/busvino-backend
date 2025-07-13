import os
import requests
from pydantic import BaseModel, EmailStr, Field
from fastapi import HTTPException
from typing import Optional
from supabase_client import supabase
from fastapi.responses import JSONResponse

def create_response(success: bool, message: str, details=None, status_code=200):
    if details is None:
        details = []
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "message": message,
            "details": details
        }
    )

class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    name: str = Field(..., min_length=1)
    phone: str
    location: str
    organization_id: str | None = None  # optional

def add_user_to_organization(org_id: str, user_id: str, mgmt_token: str):
    url = f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/organizations/{org_id}/members"
    headers = {
        "Authorization": f"Bearer {mgmt_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "members": [user_id]
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 204:
        raise HTTPException(status_code=400, detail=f"Failed to add user to org: {response.text}")

def save_user_to_supabase(auth0_user_id: str, email: str, name: str = "", phone: str = "", location: str = "", org_id: Optional[str] = None):
    user_data = {
        "auth0_id": auth0_user_id,
        "email": email,
        "name": name,
        "phone": phone,
        "location": location,
        "role": "user",
        "organization_id": org_id  # Save org_id if provided
    }

    result = supabase.table("users").insert(user_data).execute()
    return result.data

def get_management_token():
    url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    payload = {
        "client_id": os.getenv("AUTH0_CLIENT_ID"),
        "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
        "audience": f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/",
        "grant_type": "client_credentials"
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def register_user(payload: RegisterInput):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    token = get_management_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "email": payload.email,
        "password": payload.password,
        "connection": "Username-Password-Authentication"
    }

    response = requests.post(f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/users", json=data, headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail=response.json())

    user_info = response.json()
    auth0_id = user_info["user_id"]
    email = user_info["email"]

    auth0_org_id = None 
    if payload.organization_id:
        add_user_to_organization(payload.organization_id, auth0_id, token)
        auth0_org_id = payload.organization_id; 

    supabase_user = save_user_to_supabase(
        auth0_user_id=auth0_id,
        email=email,
        name=payload.name,
        phone=payload.phone,
        location=payload.location,
        org_id=auth0_org_id
    )

    data = {
        "auth0_user": user_info,
        "supabase_user": supabase_user,
    }

    return create_response(
        success=True,
        message="User created",
        details=[data],  # wrap your success data in a list for consistency
        status_code=201
    )
