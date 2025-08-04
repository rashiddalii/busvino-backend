from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """Get all users (admin only)"""
    return {"message": "Users endpoint - Coming soon!"}

@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    return {"message": f"User {user_id} - Coming soon!"} 