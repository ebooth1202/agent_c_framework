"""
Main Health Check Endpoint.

Provides a simple health check endpoint at the API root level for monitoring systems.
This endpoint gives a quick overview of system health including Redis connectivity.
"""

import time
from typing import Dict, Any
from fastapi import APIRouter

from agent_c_api.config.redis_config import RedisConfig

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Main application health check endpoint.
    
    This endpoint provides a quick overview of system health including:
    - Overall application status
    - Redis connectivity status
    - Basic system information
    
    This is designed for monitoring systems that need a simple pass/fail health check.
    For detailed Redis monitoring, use the /api/v2/debug/health/redis endpoints.
    
    Returns:
        Simple health status dictionary
    """
    health_status = {
        "status": "unknown",
        "timestamp": time.time(),
        "version": "2.0",
        "services": {}
    }
    
    # Check Redis connectivity
    redis_status = await _check_redis_health()
    health_status["services"]["redis"] = redis_status
    
    # Determine overall status
    if redis_status["status"] == "healthy":
        health_status["status"] = "healthy"
    elif redis_status["status"] == "degraded":
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe.
    
    Checks if the application is ready to serve traffic.
    This includes checking that all required dependencies are available.
    
    Returns:
        Readiness status
    """
    ready_status = {
        "ready": False,
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check Redis (required for session management)
    redis_check = await _check_redis_health()
    ready_status["checks"]["redis"] = redis_check
    
    # Application is ready if Redis is healthy or degraded (can still serve some traffic)
    ready_status["ready"] = redis_check["status"] in ["healthy", "degraded"]
    
    return ready_status


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes-style liveness probe.
    
    Checks if the application is alive and should not be restarted.
    This is a basic check that the application process is running.
    
    Returns:
        Liveness status
    """
    return {
        "alive": True,
        "timestamp": time.time(),
        "version": "2.0"
    }


async def _check_redis_health() -> Dict[str, Any]:
    """
    Quick Redis health check for the main health endpoint.
    
    Returns:
        Simple Redis health status
    """
    try:
        status = await RedisConfig.validate_connection()
        
        if status["connected"]:
            return {
                "status": "healthy",
                "connected": True,
                "host": status["host"],
                "port": status["port"]
            }
        else:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": status.get("error", "Connection failed"),
                "host": status["host"],
                "port": status["port"]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }