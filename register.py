import os
import requests
from pydantic import BaseModel, EmailStr, Field
from fastapi import HTTPException

from supabase_client import supabase

class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    name: str = Field(..., min_length=1)
    phone: str
    location: str

def save_user_to_supabase(auth0_user_id: str, email: str, name: str = "", phone: str = "", location: str = ""):
    user_data = {
        "auth0_id": auth0_user_id,
        "email": email,
        "name": name,
        "phone": phone,
        "location": location,
        "role": "user"
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
    url = f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "email": payload.email,
        "password": payload.password,
        "connection": "Username-Password-Authentication"
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail=response.json())
    
    # After Auth0 user created successfully
    user_info = response.json()
    auth0_id = user_info["user_id"]
    email = user_info["email"]

    # Save to Supabase
    supabase_user = save_user_to_supabase(
        auth0_user_id=auth0_id,
        email=email,
        name=payload.name,
        phone=payload.phone,
        location=payload.location
    )

    return {"message": "User created", "auth0_user": user_info, "supabase_user": supabase_user}
