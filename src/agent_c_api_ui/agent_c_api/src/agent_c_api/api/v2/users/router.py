# //api/src/agent_c_api/api/v2/users/router.py


from fastapi import APIRouter, Depends, HTTPException
from typing import List
from agent_c.models.chat_history.user import ChatUser
from ....core.services.user_service import UserService
from ....core.repositories.user_repository import UserRepository
from ....config.redis_config import RedisConfig

router = APIRouter(prefix="/users", tags=["users"])

async def get_user_service():
    redis_client = await RedisConfig.get_redis_client()
    user_repository = UserRepository(redis_client)
    return UserService(user_repository)

@router.post("/", response_model=ChatUser)
async def create_user(
    user: ChatUser,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user."""
    return await user_service.add_user(user)

@router.get("/{user_id}", response_model=ChatUser)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get a user by ID."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=ChatUser)
async def update_user(
    user_id: str,
    user: ChatUser,
    user_service: UserService = Depends(get_user_service)
):
    """Update a user."""
    if user_id != user.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return await user_service.update_user(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Delete a user."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}