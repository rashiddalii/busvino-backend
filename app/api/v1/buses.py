from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_buses():
    """Get all buses"""
    return {"message": "Buses endpoint - Coming soon!"}

@router.post("/")
async def create_bus():
    """Create a new bus"""
    return {"message": "Create bus - Coming soon!"} 