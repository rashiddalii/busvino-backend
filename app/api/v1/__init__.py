from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .buses import router as buses_router
from .routes import router as routes_router
from .schedules import router as schedules_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(buses_router, prefix="/buses", tags=["Buses"])
api_router.include_router(routes_router, prefix="/routes", tags=["Routes"])
api_router.include_router(schedules_router, prefix="/schedules", tags=["Schedules"]) 