from fastapi import FastAPI, Depends
from auth import get_current_user, Auth0User
from register import register_user, RegisterInput
from login import login_user, LoginInput

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI with Auth0 is working!"}


@app.post("/register")
def register(payload: RegisterInput):
    return register_user(payload)

@app.post("/login")
def login(payload: LoginInput):
    return login_user(payload)

@app.get("/protected")
def protected_route(current_user: Auth0User = Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user": current_user.dict()
    }
