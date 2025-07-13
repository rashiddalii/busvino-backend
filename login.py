import os
import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import jwt
from supabase import create_client, Client

# Setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

class LoginInput(BaseModel):
    email: str
    password: str

def login_user(payload: LoginInput):
    # Step 1: Auth0 login
    url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    data = {
        "grant_type": "password",
        "username": payload.email,
        "password": payload.password,
        "audience": os.getenv("API_AUDIENCE"),
        "client_id": os.getenv("AUTH0_CLIENT_ID"),
        "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
        "scope": "openid email profile"
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail=response.json())

    tokens = response.json()

    # Step 2: Decode ID token to get Auth0 user ID
    id_token = tokens["id_token"]
    decoded_token = jwt.decode(
        id_token,
        key=None,
        options={"verify_signature": False, "verify_aud": False}
    )

    auth0_id = decoded_token["sub"]

    # Step 3: Check Supabase
    supabase_result = supabase.table("users").select("*").eq("auth0_id", auth0_id).execute()
    if not supabase_result.data:
        raise HTTPException(status_code=404, detail="User not found in Supabase")

    return create_response(
        success=True,
        message="Login successful",
        details=[{
            "tokens": tokens,
            "supabase_user": supabase_result.data[0]
        }],
        status_code=200
    )
