"""
Repository dependency injection functions.

This module provides FastAPI dependencies for repository classes,
separated from the main dependencies module to avoid circular imports.
"""

from fastapi import Depends
from typing import Optional
from redis import asyncio as aioredis

# Import Redis dependencies directly to avoid circular imports
from agent_c_api.config.redis_config import RedisConfig
from .session_repository import SessionRepository
from .user_repository import UserRepository
from .chat_repository import ChatRepository


async def get_session_repository() -> SessionRepository:
    """
    FastAPI dependency that provides a SessionRepository.
    
    This dependency creates a SessionRepository with a Redis client,
    failing fast if Redis is not available.
        
    Returns:
        SessionRepository instance
    """
    redis_client = await RedisConfig.get_client()
    return SessionRepository(redis_client)


async def get_session_repository_optional() -> Optional[SessionRepository]:
    """
    FastAPI dependency that provides an optional SessionRepository.
    
    This dependency provides graceful degradation when Redis is not available,
    returning None instead of raising an exception.
        
    Returns:
        SessionRepository instance if Redis is available, None otherwise
    """
    try:
        redis_client = await RedisConfig.get_client()
        return SessionRepository(redis_client)
    except Exception:
        return None


async def get_user_repository() -> UserRepository:
    """
    FastAPI dependency that provides a UserRepository.
    
    This dependency creates a UserRepository with a Redis client,
    failing fast if Redis is not available.
        
    Returns:
        UserRepository instance
    """
    redis_client = await RedisConfig.get_client()
    return UserRepository(redis_client)


async def get_user_repository_optional() -> Optional[UserRepository]:
    """
    FastAPI dependency that provides an optional UserRepository.
    
    This dependency provides graceful degradation when Redis is not available,
    returning None instead of raising an exception.
        
    Returns:
        UserRepository instance if Redis is available, None otherwise
    """
    try:
        redis_client = await RedisConfig.get_client()
        return UserRepository(redis_client)
    except Exception:
        return None


# Note: ChatRepository dependencies are not included here because ChatRepository
# requires a session_id parameter that comes from the endpoint path, not from
# dependency injection. ChatService handles ChatRepository creation directly
# using the injected Redis client.