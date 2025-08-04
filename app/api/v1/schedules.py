from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_schedules():
    """Get all schedules"""
    return {"message": "Schedules endpoint - Coming soon!"}

@router.post("/")
async def create_schedule():
    """Create a new schedule"""
    return {"message": "Create schedule - Coming soon!"} 