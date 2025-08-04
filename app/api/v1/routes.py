from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_routes():
    """Get all routes"""
    return {"message": "Routes endpoint - Coming soon!"}

@router.post("/")
async def create_route():
    """Create a new route"""
    return {"message": "Create route - Coming soon!"} 