# Redis Architecture Documentation

## Overview

The Agent C API uses Redis as a high-performance, in-memory data store for session management, user data, and caching. This document describes the Redis architecture, configuration, and integration patterns used throughout the application.

## Architecture Principles

### External Redis Management
- **No Embedded Redis**: The application no longer starts or manages Redis servers
- **External Dependency**: Redis must be provided as an external service (Docker, cloud service, etc.)
- **Production Ready**: Designed for containerized and cloud deployments

### Dependency Injection Pattern
- **FastAPI Dependencies**: Redis clients are injected via FastAPI's dependency injection system
- **Multiple Variants**: Different dependency types for different error handling strategies
- **Resource Management**: Automatic connection pooling and cleanup

### Graceful Degradation
- **Optional Dependencies**: Some endpoints can function without Redis
- **Clear Error Handling**: Appropriate HTTP status codes and error messages
- **Health Monitoring**: Comprehensive health checks and monitoring

## Redis Integration Components

### 1. Configuration (`config/redis_config.py`)

**RedisConfig Class:**
- `get_redis_client()` - Creates Redis client with connection pooling
- `validate_connection()` - Validates Redis connectivity and returns status
- `close_client()` - Properly closes Redis connections

**Features:**
- Connection pooling with configurable limits
- Timeout handling for connections and operations
- Comprehensive error handling and logging
- Server information retrieval and validation

### 2. Dependency Injection (`api/dependencies.py`)

**Redis Client Dependencies:**

```python
# Standard Redis client (fails fast with HTTP 503)
get_redis_client() -> aioredis.Redis

# Optional Redis client (graceful degradation)
get_redis_client_optional() -> Optional[aioredis.Redis]

# Managed Redis client (automatic cleanup)
get_redis_client_managed() -> RedisClientManager
```

**Repository Dependencies:**

```python
# Session repository with Redis dependency
get_session_repository() -> SessionRepository

# Optional session repository
get_session_repository_optional() -> Optional[SessionRepository]

# User repository with Redis dependency
get_user_repository() -> UserRepository

# Optional user repository
get_user_repository_optional() -> Optional[UserRepository]
```

### 3. Repository Layer (`core/repositories/`)

**SessionRepository:**
- Session creation, retrieval, and management
- Session metadata and state persistence
- Session cleanup and expiration handling

**UserRepository:**
- User data storage and retrieval
- User session associations
- User preference management

**ChatRepository:**
- Chat history persistence
- Message storage and retrieval
- Session-specific chat data

### 4. Service Layer (`api/v2/*/services.py`)

**Service Integration:**
- Services receive repositories via dependency injection
- No direct Redis client creation in service layer
- Consistent error handling through dependency chain

**Examples:**
- `SessionService` - Uses `SessionRepository` for session management
- `UserService` - Uses `UserRepository` for user data operations
- `ChatService` - Uses Redis client to create session-specific repositories

### 5. Health Monitoring (`api/v2/health.py`, `api/v2/debug/health.py`)

**Health Check Levels:**
- **Basic Health** (`/api/v2/health`) - Simple connectivity check
- **Detailed Diagnostics** (`/api/v2/debug/health/redis`) - Comprehensive monitoring

**Monitoring Features:**
- Connection status and server information
- Performance metrics (latency, throughput)
- Connection pool status and metrics
- Operational health with actual Redis operations
- Warning detection for concerning metrics

## Data Storage Patterns

### Session Management
```
Key Pattern: session:{session_id}
Data: JSON serialized session metadata
TTL: Configurable (default 24 hours)
```

### User Data
```
Key Pattern: user:{user_id}
Data: JSON serialized user information
TTL: Long-term or persistent
```

### Chat History
```
Key Pattern: chat:{session_id}:{message_id}
Data: JSON serialized chat messages
TTL: Tied to session TTL
```

### Temporary Data
```
Key Pattern: temp:{operation_id}
Data: Temporary operation data
TTL: Short-term (minutes to hours)
```

## Error Handling Strategy

### Connection Failures
- **Fail Fast**: Critical endpoints return HTTP 503 when Redis unavailable
- **Graceful Degradation**: Optional endpoints continue with reduced functionality
- **Clear Messaging**: Detailed error messages for troubleshooting

### Timeout Handling
- **Connection Timeouts**: Configurable connection establishment timeouts
- **Operation Timeouts**: Configurable operation execution timeouts
- **Retry Logic**: Built into Redis client connection pooling

### Data Consistency
- **Atomic Operations**: Use Redis transactions where needed
- **Expiration Policies**: Consistent TTL management
- **Cleanup Procedures**: Regular cleanup of expired data

## Performance Optimization

### Connection Pooling
```python
# Configuration
REDIS_MAX_CONNECTIONS=50      # Maximum connections in pool
REDIS_CONNECTION_TIMEOUT=5    # Connection timeout in seconds
REDIS_SOCKET_TIMEOUT=5        # Socket timeout in seconds
```

### Memory Management
- **TTL Policies**: Automatic expiration of temporary data
- **Cleanup Jobs**: Regular cleanup of expired sessions
- **Memory Monitoring**: Health checks monitor Redis memory usage

### Operation Efficiency
- **Pipelining**: Batch operations where possible
- **Lua Scripts**: Complex operations executed server-side
- **Key Design**: Efficient key patterns for fast lookups

## Security Considerations

### Authentication
```python
# Redis AUTH configuration
REDIS_USERNAME=username       # Redis 6+ username
REDIS_PASSWORD=password       # Redis password
```

### Network Security
- **VPC/Private Networks**: Redis should not be publicly accessible
- **TLS Encryption**: Use Redis TLS for encrypted connections
- **Firewall Rules**: Restrict Redis port access

### Data Protection
- **Sensitive Data**: Avoid storing sensitive data in Redis
- **Encryption**: Consider application-level encryption for sensitive data
- **Access Control**: Use Redis ACLs for fine-grained access control

## Deployment Patterns

### Development Environment
```yaml
# Docker Compose
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

### Production Environment
```yaml
# Kubernetes
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
```

### Cloud Services
- **AWS ElastiCache**: Managed Redis with automatic failover
- **Azure Cache for Redis**: Fully managed Redis service
- **Google Cloud Memorystore**: Managed Redis with VPC integration

## Monitoring and Observability

### Health Endpoints
- `/api/v2/health` - Basic application health including Redis
- `/api/v2/health/ready` - Kubernetes readiness probe
- `/api/v2/health/live` - Kubernetes liveness probe
- `/api/v2/debug/health/redis` - Detailed Redis diagnostics

### Metrics Collection
- **Connection Pool Metrics**: Active/available connections
- **Performance Metrics**: Latency, throughput, hit ratios
- **Error Metrics**: Connection failures, timeout rates
- **Resource Metrics**: Memory usage, key counts

### Alerting
- **Critical**: Redis connectivity failures
- **Warning**: High latency, low hit ratios, memory pressure
- **Info**: Connection pool utilization, cleanup operations

## Migration and Upgrades

### From Embedded Redis
1. **Setup External Redis**: Deploy Redis service
2. **Update Configuration**: Point to external Redis
3. **Remove Deprecated Settings**: Clean up old configuration
4. **Test Connectivity**: Verify health endpoints
5. **Data Migration**: Sessions recreate automatically

### Redis Version Upgrades
1. **Compatibility Check**: Verify client compatibility
2. **Staged Deployment**: Upgrade non-production first
3. **Health Monitoring**: Monitor during upgrade
4. **Rollback Plan**: Prepare rollback procedures

## Troubleshooting

### Common Issues

**Connection Refused:**
```bash
# Check Redis status
redis-cli -h localhost -p 6379 ping

# Check network connectivity
telnet redis-host 6379
```

**High Latency:**
```bash
# Monitor Redis performance
redis-cli --latency -h redis-host -p 6379

# Check network latency
ping redis-host
```

**Memory Issues:**
```bash
# Check Redis memory usage
redis-cli -h redis-host -p 6379 info memory

# Monitor key expiration
redis-cli -h redis-host -p 6379 info keyspace
```

### Diagnostic Tools
- **Health Endpoints**: Use API health checks for status
- **Redis CLI**: Direct Redis server diagnostics
- **Application Logs**: Detailed error information
- **Monitoring Dashboards**: Performance visualization

## Best Practices

### Configuration
- Use environment variables for all Redis settings
- Set appropriate timeouts for your network environment
- Configure connection pooling based on expected load
- Enable Redis persistence for important data

### Development
- Use dependency injection for all Redis access
- Implement proper error handling for Redis failures
- Write tests with mocked Redis dependencies
- Use health checks to verify Redis connectivity

### Operations
- Monitor Redis health and performance continuously
- Set up alerting for critical Redis metrics
- Implement backup and recovery procedures
- Plan for Redis maintenance and upgrades

### Security
- Never expose Redis directly to the internet
- Use strong authentication credentials
- Enable TLS encryption for production
- Regularly rotate Redis passwords