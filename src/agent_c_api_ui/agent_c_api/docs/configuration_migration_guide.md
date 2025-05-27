# Configuration Migration Guide

## Overview

This guide helps you migrate from the old embedded Redis configuration to the new external Redis architecture introduced in the Redis refactor.

## What Changed

### Removed Features
- **Embedded Redis Server**: The API no longer starts or manages Redis servers
- **Redis Lifecycle Management**: No more automatic Redis startup/shutdown
- **Local Redis Data Directory**: Redis data is now managed externally

### New Features
- **External Redis Dependency**: Redis must be provided as a separate service
- **Enhanced Connection Management**: Better connection pooling and error handling
- **Health Monitoring**: Comprehensive Redis health checks and monitoring
- **Production Readiness**: Designed for containerized and cloud deployments

## Configuration Changes

### Deprecated Settings

The following settings are **deprecated** and **ignored** by the application:

```python
# DEPRECATED - No longer used
REDIS_DATA_DIR = "./data/redis"        # Use external Redis
REDIS_STARTUP_TIMEOUT = 30            # No embedded Redis startup
MANAGE_REDIS_LIFECYCLE = True         # Always False - external Redis only
```

### New Settings

The following settings have been **added** for better Redis management:

```python
# New connection pool settings
REDIS_CONNECTION_TIMEOUT = 5          # Connection timeout in seconds
REDIS_SOCKET_TIMEOUT = 5              # Socket timeout in seconds  
REDIS_MAX_CONNECTIONS = 50            # Maximum connections in pool
```

### Updated Environment Variables

**Before (Old Configuration):**
```bash
# Old embedded Redis settings
REDIS_DATA_DIR=./data/redis
REDIS_STARTUP_TIMEOUT=30
MANAGE_REDIS_LIFECYCLE=true

# Basic connection settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

**After (New Configuration):**
```bash
# External Redis connection (required)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Optional authentication
REDIS_USERNAME=
REDIS_PASSWORD=

# New connection pool settings
REDIS_CONNECTION_TIMEOUT=5
REDIS_SOCKET_TIMEOUT=5
REDIS_MAX_CONNECTIONS=50

# Session management
SESSION_TTL=86400
SESSION_CLEANUP_INTERVAL=3600
USE_REDIS_SESSIONS=true
```

## Migration Steps

### 1. Setup External Redis

Choose one of the following Redis deployment options:

#### Option A: Docker (Recommended for Development)
```bash
# Start Redis container
docker run -d --name redis -p 6379:6379 redis:7-alpine

# With persistence
docker run -d --name redis -p 6379:6379 -v redis_data:/data redis:7-alpine redis-server --appendonly yes

# With password
docker run -d --name redis -p 6379:6379 redis:7-alpine redis-server --requirepass mypassword
```

#### Option B: Native Installation
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install redis-server
sudo systemctl enable redis-server && sudo systemctl start redis-server

# CentOS/RHEL
sudo yum install epel-release && sudo yum install redis
sudo systemctl enable redis && sudo systemctl start redis

# macOS
brew install redis && brew services start redis
```

#### Option C: Cloud Service
- **AWS ElastiCache**: Managed Redis with automatic failover
- **Azure Cache for Redis**: Fully managed Redis service
- **Google Cloud Memorystore**: Managed Redis with VPC integration

### 2. Update Configuration

#### Update Environment File
Create or update your `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit with your Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# Add REDIS_PASSWORD if using authentication
```

#### Remove Deprecated Settings
Remove or comment out deprecated settings from your configuration:

```bash
# Remove these lines from .env
# REDIS_DATA_DIR=./data/redis
# REDIS_STARTUP_TIMEOUT=30
# MANAGE_REDIS_LIFECYCLE=true
```

### 3. Test Connectivity

#### Verify Redis Connection
```bash
# Test Redis directly
redis-cli ping
# Expected: PONG

# Test with authentication (if configured)
redis-cli -a yourpassword ping
```

#### Test API Health
```bash
# Start the API
python -m uvicorn agent_c_api.main:app --reload

# Test health endpoint
curl http://localhost:8000/api/v2/health
# Expected: {"status": "healthy", ...}

# Detailed Redis diagnostics
curl http://localhost:8000/api/v2/debug/health/redis
```

### 4. Data Migration (If Needed)

#### Session Data
- **Automatic Recreation**: User sessions will be recreated automatically
- **No Manual Migration**: Session data is transient and doesn't require migration
- **User Impact**: Users may need to re-authenticate

#### Persistent Data
If you have custom persistent data in the old Redis:

```bash
# Export data from old Redis (if accessible)
redis-cli --rdb dump.rdb

# Import to new Redis (if needed)
redis-cli --pipe < dump.rdb
```

### 5. Update Deployment

#### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

#### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-c-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: agent-c-api:latest
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        livenessProbe:
          httpGet:
            path: /api/v2/health/live
            port: 8000
        readinessProbe:
          httpGet:
            path: /api/v2/health/ready
            port: 8000
```

## Verification Checklist

### ✅ Pre-Migration Checklist
- [ ] External Redis service is running and accessible
- [ ] Redis authentication is configured (if required)
- [ ] Network connectivity between API and Redis is verified
- [ ] Backup of existing data is created (if needed)

### ✅ Configuration Checklist
- [ ] `.env` file is updated with new Redis settings
- [ ] Deprecated settings are removed or commented out
- [ ] New connection pool settings are configured
- [ ] Session management settings are configured

### ✅ Testing Checklist
- [ ] Redis connectivity test passes (`redis-cli ping`)
- [ ] API health check returns healthy status
- [ ] Detailed Redis diagnostics show all green
- [ ] API can create and retrieve sessions
- [ ] Application functionality works as expected

### ✅ Production Checklist
- [ ] Redis is properly secured (authentication, network)
- [ ] Redis persistence is configured for data durability
- [ ] Monitoring and alerting are set up
- [ ] Backup and recovery procedures are in place
- [ ] Load testing has been performed

## Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if Redis is running
redis-cli ping
# If fails: Start Redis service

# Check network connectivity
telnet redis-host 6379
# If fails: Check firewall/network settings
```

#### Authentication Errors
```bash
# Test Redis authentication
redis-cli -h localhost -p 6379 -a yourpassword ping
# If fails: Check REDIS_PASSWORD setting
```

#### Health Check Failures
```bash
# Check API health endpoint
curl http://localhost:8000/api/v2/health
# If unhealthy: Check Redis connectivity and logs

# Check detailed diagnostics
curl http://localhost:8000/api/v2/debug/health/redis
# Review error messages for specific issues
```

#### High Latency
```bash
# Monitor Redis latency
redis-cli --latency -h redis-host -p 6379

# Check network latency
ping redis-host

# Review connection pool settings
# Consider increasing REDIS_MAX_CONNECTIONS
```

### Log Analysis

#### API Startup Logs
Look for Redis connection status in startup logs:
```
✅ Redis connection validated successfully at localhost:6379
🔍 Redis Server Info: version=7.0.0, mode=standalone, memory=1.2MB
```

#### Error Logs
Common error patterns:
```
❌ Redis connection failed: Connection refused
❌ Redis connection timeout: timed out
❌ Redis authentication failed: invalid password
```

### Recovery Procedures

#### Redis Service Recovery
```bash
# Restart Redis service
sudo systemctl restart redis

# For Docker
docker restart redis

# Check Redis logs
sudo journalctl -u redis
docker logs redis
```

#### API Recovery
```bash
# Restart API service
sudo systemctl restart agent-c-api

# Check API health after restart
curl http://localhost:8000/api/v2/health
```

## Performance Tuning

### Connection Pool Optimization
```bash
# Monitor connection usage
curl http://localhost:8000/api/v2/debug/health/redis/connection-pool

# Adjust based on load
REDIS_MAX_CONNECTIONS=100  # For high-traffic environments
REDIS_CONNECTION_TIMEOUT=10  # For high-latency networks
```

### Redis Configuration
```bash
# Redis memory optimization
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru

# Redis persistence tuning
redis-cli config set save "900 1 300 10 60 10000"
```

## Support and Resources

### Documentation
- [Redis Architecture](redis_architecture.md) - Detailed architecture documentation
- [Environment Configuration](environment_configuration.md) - Complete configuration guide
- [V2 API Documentation](v2_api_documentation.md) - API reference

### Health Monitoring
- `/api/v2/health` - Basic health check
- `/api/v2/debug/health/redis` - Detailed Redis diagnostics
- `/api/v2/health/ready` - Kubernetes readiness probe
- `/api/v2/health/live` - Kubernetes liveness probe

### Community Support
- Check application logs for detailed error information
- Use health endpoints for operational diagnostics
- Review Redis server logs for connection issues
- Monitor Redis performance metrics for optimization

## Migration Timeline

### Recommended Migration Phases

#### Phase 1: Development Environment (Week 1)
- Set up external Redis in development
- Update configuration and test locally
- Verify all functionality works correctly

#### Phase 2: Staging Environment (Week 2)
- Deploy external Redis in staging
- Update staging configuration
- Perform comprehensive testing
- Load testing and performance validation

#### Phase 3: Production Environment (Week 3)
- Deploy external Redis in production
- Update production configuration
- Monitor health and performance
- Gradual rollout with rollback plan

This phased approach ensures a smooth migration with minimal risk to production systems.