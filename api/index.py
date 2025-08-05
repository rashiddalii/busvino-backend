from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.core.auth import get_auth0_user
from app.schemas.common import APIResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.utils.handlers import validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import app.api.v1.auth as auth_router
import app.api.v1.users as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Bus Tracking API...")
    yield
    # Shutdown
    print("👋 Shutting down Bus Tracking API...")

# Create FastAPI app
app = FastAPI(
    title="Bus Tracking API",
    description="API for Bus Tracking SaaS",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI with Auth0 is working!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Include routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["User Management"])

@app.post("/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    auth_service = AuthService()
    return await auth_service.register_user(request)

@app.post("/login") 
async def login(request: LoginRequest):
    """Login user"""
    auth_service = AuthService()
    return await auth_service.login_user(request)

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_auth0_user)):
    """Protected route example"""
    return {
        "message": "Access granted",
        "user": current_user
    }