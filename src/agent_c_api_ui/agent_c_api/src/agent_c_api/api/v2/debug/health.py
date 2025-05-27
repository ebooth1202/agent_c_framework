"""
Redis Health Check and Monitoring Endpoints.

Provides comprehensive Redis health monitoring including:
- Basic connectivity checks
- Performance metrics
- Connection pool status
- Server information and metrics
- Operational health indicators
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError

from agent_c_api.api.dependencies import get_redis_client_optional
from agent_c_api.config.redis_config import RedisConfig
from agent_c_api.config.env_config import settings

router = APIRouter(prefix="/health", tags=["redis-health"])


@router.get("/redis")
async def redis_health_check() -> Dict[str, Any]:
    """
    Comprehensive Redis health check endpoint.
    
    Returns detailed health information including:
    - Connection status
    - Server information
    - Performance metrics
    - Connection pool status
    - Operational indicators
    
    Returns:
        Comprehensive health status dictionary
    """
    health_status = {
        "status": "unknown",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Basic connectivity check
    connectivity_check = await _check_connectivity()
    health_status["checks"]["connectivity"] = connectivity_check
    
    # Performance metrics
    performance_check = await _check_performance()
    health_status["checks"]["performance"] = performance_check
    
    # Server information
    server_info_check = await _check_server_info()
    health_status["checks"]["server_info"] = server_info_check
    
    # Connection pool metrics
    pool_check = await _check_connection_pool()
    health_status["checks"]["connection_pool"] = pool_check
    
    # Operational health
    operational_check = await _check_operational_health()
    health_status["checks"]["operational"] = operational_check
    
    # Determine overall status
    health_status["status"] = _determine_overall_status(health_status["checks"])
    
    return health_status


@router.get("/redis/connectivity")
async def redis_connectivity_check() -> Dict[str, Any]:
    """
    Basic Redis connectivity check.
    
    Returns:
        Connection status and basic information
    """
    return await _check_connectivity()


@router.get("/redis/performance")
async def redis_performance_check() -> Dict[str, Any]:
    """
    Redis performance metrics check.
    
    Returns:
        Performance metrics including latency and throughput
    """
    return await _check_performance()


@router.get("/redis/server-info")
async def redis_server_info_check() -> Dict[str, Any]:
    """
    Redis server information check.
    
    Returns:
        Detailed server information and statistics
    """
    return await _check_server_info()


@router.get("/redis/connection-pool")
async def redis_connection_pool_check() -> Dict[str, Any]:
    """
    Redis connection pool status check.
    
    Returns:
        Connection pool metrics and status
    """
    return await _check_connection_pool()


@router.get("/redis/operational")
async def redis_operational_check() -> Dict[str, Any]:
    """
    Redis operational health check.
    
    Returns:
        Operational health indicators
    """
    return await _check_operational_health()


async def _check_connectivity() -> Dict[str, Any]:
    """Check basic Redis connectivity."""
    check = {
        "name": "connectivity",
        "status": "unknown",
        "details": {},
        "error": None
    }
    
    try:
        # Use the existing validation method
        status = await RedisConfig.validate_connection()
        
        if status["connected"]:
            check["status"] = "healthy"
            check["details"] = {
                "host": status["host"],
                "port": status["port"],
                "db": status["db"],
                "connected": True
            }
        else:
            check["status"] = "unhealthy"
            check["error"] = status.get("error", "Connection failed")
            check["details"] = {
                "host": status["host"],
                "port": status["port"],
                "db": status["db"],
                "connected": False
            }
            
    except Exception as e:
        check["status"] = "error"
        check["error"] = str(e)
        
    return check


async def _check_performance() -> Dict[str, Any]:
    """Check Redis performance metrics."""
    check = {
        "name": "performance",
        "status": "unknown",
        "details": {},
        "error": None
    }
    
    try:
        redis = await RedisConfig.get_redis_client()
        
        # Measure ping latency
        start_time = time.time()
        await redis.ping()
        ping_latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Measure simple operation latency
        start_time = time.time()
        test_key = f"health_check_{int(time.time())}"
        await redis.set(test_key, "test_value", ex=60)
        await redis.get(test_key)
        await redis.delete(test_key)
        operation_latency = (time.time() - start_time) * 1000
        
        check["status"] = "healthy"
        check["details"] = {
            "ping_latency_ms": round(ping_latency, 2),
            "operation_latency_ms": round(operation_latency, 2),
            "latency_status": _evaluate_latency(ping_latency)
        }
        
        # Mark as unhealthy if latency is too high
        if ping_latency > 1000:  # 1 second
            check["status"] = "unhealthy"
            check["error"] = f"High latency detected: {ping_latency:.2f}ms"
            
    except Exception as e:
        check["status"] = "error"
        check["error"] = str(e)
        
    return check


async def _check_server_info() -> Dict[str, Any]:
    """Check Redis server information and statistics."""
    check = {
        "name": "server_info",
        "status": "unknown",
        "details": {},
        "error": None
    }
    
    try:
        redis = await RedisConfig.get_redis_client()
        info = await redis.info()
        
        # Extract key metrics
        server_details = {
            "redis_version": info.get("redis_version"),
            "redis_mode": info.get("redis_mode"),
            "used_memory_human": info.get("used_memory_human"),
            "used_memory_peak_human": info.get("used_memory_peak_human"),
            "connected_clients": info.get("connected_clients"),
            "blocked_clients": info.get("blocked_clients"),
            "uptime_in_seconds": info.get("uptime_in_seconds"),
            "uptime_in_days": info.get("uptime_in_days"),
            "total_commands_processed": info.get("total_commands_processed"),
            "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "expired_keys": info.get("expired_keys"),
            "evicted_keys": info.get("evicted_keys")
        }
        
        # Calculate hit ratio
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total_requests = hits + misses
        hit_ratio = (hits / total_requests * 100) if total_requests > 0 else 0
        
        server_details["hit_ratio_percent"] = round(hit_ratio, 2)
        
        check["status"] = "healthy"
        check["details"] = server_details
        
        # Check for concerning metrics
        warnings = []
        if info.get("connected_clients", 0) > 100:
            warnings.append(f"High client count: {info.get('connected_clients')}")
        if hit_ratio < 80 and total_requests > 100:
            warnings.append(f"Low hit ratio: {hit_ratio:.1f}%")
        if info.get("evicted_keys", 0) > 0:
            warnings.append(f"Keys being evicted: {info.get('evicted_keys')}")
            
        if warnings:
            check["details"]["warnings"] = warnings
            
    except Exception as e:
        check["status"] = "error"
        check["error"] = str(e)
        
    return check


async def _check_connection_pool() -> Dict[str, Any]:
    """Check Redis connection pool status."""
    check = {
        "name": "connection_pool",
        "status": "unknown",
        "details": {},
        "error": None
    }
    
    try:
        redis = await RedisConfig.get_redis_client()
        
        # Get connection pool information
        pool = redis.connection_pool
        
        pool_details = {
            "max_connections": getattr(pool, "max_connections", "unknown"),
            "connection_class": pool.connection_class.__name__ if hasattr(pool, "connection_class") else "unknown",
            "host": getattr(pool.connection_kwargs, "host", settings.REDIS_HOST) if hasattr(pool, "connection_kwargs") else settings.REDIS_HOST,
            "port": getattr(pool.connection_kwargs, "port", settings.REDIS_PORT) if hasattr(pool, "connection_kwargs") else settings.REDIS_PORT,
            "db": getattr(pool.connection_kwargs, "db", settings.REDIS_DB) if hasattr(pool, "connection_kwargs") else settings.REDIS_DB
        }
        
        # Try to get pool statistics if available
        if hasattr(pool, "_available_connections"):
            pool_details["available_connections"] = len(pool._available_connections)
        if hasattr(pool, "_in_use_connections"):
            pool_details["in_use_connections"] = len(pool._in_use_connections)
            
        check["status"] = "healthy"
        check["details"] = pool_details
        
    except Exception as e:
        check["status"] = "error"
        check["error"] = str(e)
        
    return check


async def _check_operational_health() -> Dict[str, Any]:
    """Check operational health indicators."""
    check = {
        "name": "operational",
        "status": "unknown",
        "details": {},
        "error": None
    }
    
    try:
        redis = await RedisConfig.get_redis_client()
        
        # Test basic operations
        test_key = f"health_operational_{int(time.time())}"
        test_value = "operational_test"
        
        # Test SET operation
        set_result = await redis.set(test_key, test_value, ex=60)
        
        # Test GET operation
        get_result = await redis.get(test_key)
        
        # Test DELETE operation
        del_result = await redis.delete(test_key)
        
        # Test key existence check
        exists_result = await redis.exists(test_key)
        
        operational_details = {
            "set_operation": "success" if set_result else "failed",
            "get_operation": "success" if get_result == test_value.encode() else "failed",
            "delete_operation": "success" if del_result == 1 else "failed",
            "exists_operation": "success" if exists_result == 0 else "failed",
            "all_operations_successful": all([
                set_result,
                get_result == test_value.encode(),
                del_result == 1,
                exists_result == 0
            ])
        }
        
        if operational_details["all_operations_successful"]:
            check["status"] = "healthy"
        else:
            check["status"] = "degraded"
            check["error"] = "Some operations failed"
            
        check["details"] = operational_details
        
    except Exception as e:
        check["status"] = "error"
        check["error"] = str(e)
        
    return check


def _evaluate_latency(latency_ms: float) -> str:
    """Evaluate latency and return status."""
    if latency_ms < 10:
        return "excellent"
    elif latency_ms < 50:
        return "good"
    elif latency_ms < 100:
        return "acceptable"
    elif latency_ms < 500:
        return "poor"
    else:
        return "critical"


def _determine_overall_status(checks: Dict[str, Dict[str, Any]]) -> str:
    """Determine overall health status from individual checks."""
    statuses = [check.get("status", "unknown") for check in checks.values()]
    
    if "error" in statuses:
        return "error"
    elif "unhealthy" in statuses:
        return "unhealthy"
    elif "degraded" in statuses:
        return "degraded"
    elif all(status == "healthy" for status in statuses):
        return "healthy"
    else:
        return "unknown"