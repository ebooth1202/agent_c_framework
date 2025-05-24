"""
Redis dependency testing endpoints.

These endpoints can be used to test Redis connectivity and dependency injection.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from redis import asyncio as aioredis

from agent_c_api.api.dependencies import (
    get_redis_client,
    get_redis_client_optional,
    get_redis_client_managed,
    get_session_repository,
    get_session_repository_optional,
    RedisClientManager
)
from agent_c_api.config.redis_config import RedisConfig

router = APIRouter(prefix="/redis", tags=["redis-debug"])


@router.get("/status")
async def redis_status() -> Dict[str, Any]:
    """
    Get detailed Redis connection status.
    
    Returns:
        Dictionary with Redis status information
    """
    return await RedisConfig.validate_connection()


@router.get("/ping")
async def redis_ping(redis: aioredis.Redis = Depends(get_redis_client)) -> Dict[str, str]:
    """
    Test Redis connectivity using dependency injection.
    
    Args:
        redis: Redis client dependency
        
    Returns:
        Ping response from Redis
    """
    try:
        result = await redis.ping()
        return {"status": "success", "ping": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis ping failed: {str(e)}")


@router.get("/ping-optional")
async def redis_ping_optional(redis: Optional[aioredis.Redis] = Depends(get_redis_client_optional)) -> Dict[str, str]:
    """
    Test Redis connectivity with optional dependency.
    
    Args:
        redis: Optional Redis client dependency
        
    Returns:
        Ping response or fallback message
    """
    if redis is None:
        return {"status": "unavailable", "message": "Redis is not available"}
    
    try:
        result = await redis.ping()
        return {"status": "success", "ping": str(result)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/test-set/{key}")
async def redis_test_set(
    key: str, 
    value: str,
    redis_manager: RedisClientManager = Depends(get_redis_client_managed)
) -> Dict[str, str]:
    """
    Test Redis SET operation using managed client.
    
    Args:
        key: Redis key to set
        value: Value to store
        redis_manager: Managed Redis client dependency
        
    Returns:
        Operation result
    """
    async with redis_manager as redis:
        try:
            result = await redis.set(f"test:{key}", value, ex=300)  # 5 minute expiry
            return {
                "status": "success", 
                "key": f"test:{key}", 
                "value": value,
                "result": str(result)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Redis SET failed: {str(e)}")


@router.get("/test-get/{key}")
async def redis_test_get(
    key: str,
    redis: aioredis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Test Redis GET operation.
    
    Args:
        key: Redis key to retrieve
        redis: Redis client dependency
        
    Returns:
        Retrieved value or None
    """
    try:
        value = await redis.get(f"test:{key}")
        return {
            "status": "success",
            "key": f"test:{key}",
            "value": value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis GET failed: {str(e)}")


@router.get("/session-repository-test")
async def session_repository_test(
    session_repo = Depends(get_session_repository)
) -> Dict[str, Any]:
    """
    Test SessionRepository dependency injection.
    
    Args:
        session_repo: SessionRepository dependency
        
    Returns:
        Repository test result
    """
    try:
        # Test basic repository functionality
        # This would normally create a session, but we'll just test the dependency
        return {
            "status": "success",
            "message": "SessionRepository dependency injection working",
            "repository_type": type(session_repo).__name__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository test failed: {str(e)}")


@router.get("/session-repository-optional-test")
async def session_repository_optional_test(
    session_repo = Depends(get_session_repository_optional)
) -> Dict[str, Any]:
    """
    Test optional SessionRepository dependency injection.
    
    Args:
        session_repo: Optional SessionRepository dependency
        
    Returns:
        Repository test result
    """
    if session_repo is None:
        return {
            "status": "unavailable",
            "message": "SessionRepository not available (Redis unavailable)"
        }
    
    try:
        return {
            "status": "success",
            "message": "Optional SessionRepository dependency injection working",
            "repository_type": type(session_repo).__name__
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}