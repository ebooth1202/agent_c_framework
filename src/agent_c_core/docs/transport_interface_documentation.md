# Transport Interface Documentation

## Overview

The Transport Interface provides a clean abstraction layer for EventSessionLogger to send events to various downstream systems. This enables the gateway pattern to support multiple transport types while maintaining consistent error handling and resource management.

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│                     │    │                      │    │                     │
│  EventSessionLogger │───▶│  TransportInterface  │───▶│  Downstream System  │
│     (Gateway)       │    │    (Abstraction)     │    │  (Queue/Bus/etc.)   │
│                     │    │                      │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## TransportInterface ABC

### Core Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class TransportInterface(ABC):
    """
    Abstract base class for transport implementations.
    
    Provides consistent interface for sending events to downstream systems
    like message queues, databases, monitoring systems, etc.
    """
    
    @abstractmethod
    async def send(self, event: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send event to downstream system.
        
        Args:
            event: Event object to send
            metadata: Optional metadata (session_id, timestamp, etc.)
            
        Returns:
            bool: True if send succeeded, False otherwise
            
        Raises:
            TransportError: For transport-specific errors
        """
        pass
    
    async def connect(self) -> None:
        """Optional: Establish connection to downstream system"""
        pass
    
    async def disconnect(self) -> None:
        """Optional: Close connection to downstream system"""
        pass
    
    async def close(self) -> None:
        """Clean shutdown - close connections and resources"""
        await self.disconnect()
    
    # Context manager support
    async def __aenter__(self) -> 'TransportInterface':
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
```

## Built-in Transport Implementations

### 1. CallbackTransport

Wraps callback functions for backward compatibility and transition scenarios.

```python
from agent_c.util.transports import CallbackTransport

async def my_callback(event):
    print(f"Received: {type(event).__name__}")
    # Process event...

transport = CallbackTransport(my_callback)

# Usage with EventSessionLogger
logger = create_with_transport(
    transport=transport,
    log_base_dir="./logs"
)
```

**Features:**
- Wraps async or sync callback functions
- Automatic async/sync detection and handling
- Error isolation and retry support
- Backward compatibility with existing callback patterns

### 2. LoggingTransport

Sends events to Python logging system for debugging and development.

```python
from agent_c.util.transports import LoggingTransport
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

transport = LoggingTransport(
    logger_name="event_transport",
    log_level=logging.INFO,
    include_metadata=True
)

# Usage
logger = create_with_transport(
    transport=transport,
    log_base_dir="./logs"
)
```

**Features:**
- Integration with Python logging system
- Configurable log levels and formatting
- Metadata inclusion options
- Useful for debugging and development

### 3. NullTransport

No-op transport for testing and scenarios where downstream delivery isn't needed.

```python
from agent_c.util.transports import NullTransport

transport = NullTransport()

# Usage for testing
logger = create_with_transport(
    transport=transport,
    log_base_dir="./test_logs"
)
```

**Features:**
- No-op implementation (does nothing)
- Always returns success
- Useful for testing and development
- Zero overhead

### 4. RetryTransport

Wraps other transports with retry logic and error handling.

```python
from agent_c.util.transports import RetryTransport, CallbackTransport

# Base transport that might fail
base_transport = CallbackTransport(unreliable_callback)

# Wrap with retry logic
transport = RetryTransport(
    base_transport=base_transport,
    max_attempts=3,
    delay_seconds=1.0,
    backoff_multiplier=2.0,
    max_delay_seconds=30.0
)

# Usage
logger = create_with_transport(
    transport=transport,
    log_base_dir="./logs"
)
```

**Features:**
- Exponential backoff retry logic
- Configurable retry attempts and delays
- Error tracking and metrics
- Wraps any TransportInterface implementation

## Custom Transport Development

### Basic Custom Transport

```python
from agent_c.util.transports import TransportInterface, TransportError
import aiohttp
import json

class HTTPTransport(TransportInterface):
    """Send events to HTTP endpoint"""
    
    def __init__(self, endpoint_url: str, headers: Dict[str, str] = None):
        self.endpoint_url = endpoint_url
        self.headers = headers or {}
        self.session = None
    
    async def connect(self) -> None:
        """Establish HTTP session"""
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        """Send event via HTTP POST"""
        if not self.session:
            await self.connect()
        
        try:
            # Serialize event
            payload = {
                'event': event.dict() if hasattr(event, 'dict') else str(event),
                'metadata': metadata or {},
                'timestamp': time.time()
            }
            
            # Send to endpoint
            async with self.session.post(
                self.endpoint_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return True
                else:
                    raise TransportError(f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            raise TransportError(f"HTTP transport failed: {e}")
    
    async def disconnect(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def close(self) -> None:
        """Clean shutdown"""
        await self.disconnect()

# Usage
transport = HTTPTransport(
    endpoint_url="https://api.example.com/events",
    headers={"Authorization": "Bearer token123"}
)

logger = create_with_transport(
    transport=transport,
    log_base_dir="./logs"
)
```

### Advanced Custom Transport with Connection Pooling

```python
import asyncio
from typing import List
import redis.asyncio as redis

class RedisStreamTransport(TransportInterface):
    """Send events to Redis Streams"""
    
    def __init__(self, redis_url: str, stream_name: str = "agent_events"):
        self.redis_url = redis_url
        self.stream_name = stream_name
        self.redis_client = None
        self.connection_pool = None
    
    async def connect(self) -> None:
        """Establish Redis connection with pooling"""
        self.connection_pool = redis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=10,
            retry_on_timeout=True
        )
        self.redis_client = redis.Redis(connection_pool=self.connection_pool)
        
        # Test connection
        await self.redis_client.ping()
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        """Send event to Redis Stream"""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Prepare stream data
            stream_data = {
                'event_type': type(event).__name__,
                'session_id': getattr(event, 'session_id', 'unknown'),
                'event_data': json.dumps(event.dict() if hasattr(event, 'dict') else str(event)),
                'metadata': json.dumps(metadata or {}),
                'timestamp': str(time.time())
            }
            
            # Add to stream
            message_id = await self.redis_client.xadd(
                self.stream_name,
                stream_data,
                maxlen=10000  # Keep last 10k events
            )
            
            return message_id is not None
            
        except Exception as e:
            raise TransportError(f"Redis transport failed: {e}")
    
    async def disconnect(self) -> None:
        """Close Redis connections"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        
        if self.connection_pool:
            await self.connection_pool.disconnect()
            self.connection_pool = None
    
    async def close(self) -> None:
        """Clean shutdown"""
        await self.disconnect()

# Usage
transport = RedisStreamTransport(
    redis_url="redis://localhost:6379",
    stream_name="agent_events"
)

# Use with retry wrapper for production
retry_transport = RetryTransport(
    base_transport=transport,
    max_attempts=3,
    delay_seconds=1.0
)

logger = create_with_transport(
    transport=retry_transport,
    log_base_dir="./logs"
)
```

## Transport Integration Patterns

### 1. Single Transport Pattern

```python
# Simple single transport
transport = CallbackTransport(my_callback)
logger = create_with_transport(transport=transport, log_base_dir="./logs")
```

### 2. Multi-Transport Pattern

```python
# Multiple transports for different purposes
transports = [
    CallbackTransport(monitoring_callback),    # Real-time monitoring
    HTTPTransport("https://api.logs.com"),     # Cloud logging
    RedisStreamTransport("redis://localhost")  # Event streaming
]

logger = create_multi_transport_logger(
    log_base_dir="./logs",
    transports=transports
)
```

### 3. Fallback Transport Pattern

```python
# Primary transport with fallback
class FallbackTransport(TransportInterface):
    def __init__(self, primary: TransportInterface, fallback: TransportInterface):
        self.primary = primary
        self.fallback = fallback
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        try:
            return await self.primary.send(event, metadata)
        except TransportError:
            # Fallback to secondary transport
            return await self.fallback.send(event, metadata)

# Usage
primary = HTTPTransport("https://primary.api.com")
fallback = RedisStreamTransport("redis://localhost")
transport = FallbackTransport(primary, fallback)

logger = create_with_transport(transport=transport, log_base_dir="./logs")
```

### 4. Load Balancing Transport Pattern

```python
import random

class LoadBalancingTransport(TransportInterface):
    def __init__(self, transports: List[TransportInterface]):
        self.transports = transports
        self.current_index = 0
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        # Round-robin load balancing
        transport = self.transports[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.transports)
        
        return await transport.send(event, metadata)

# Usage
transports = [
    HTTPTransport("https://endpoint1.com"),
    HTTPTransport("https://endpoint2.com"),
    HTTPTransport("https://endpoint3.com")
]

transport = LoadBalancingTransport(transports)
logger = create_with_transport(transport=transport, log_base_dir="./logs")
```

## Error Handling and Resilience

### Transport Exceptions

```python
from agent_c.util.transport_exceptions import (
    TransportError,
    ConnectionError,
    TimeoutError,
    SerializationError
)

class RobustTransport(TransportInterface):
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        try:
            # Attempt to send
            return await self._do_send(event, metadata)
            
        except ConnectionError as e:
            # Handle connection issues
            await self._handle_connection_error(e)
            raise
            
        except TimeoutError as e:
            # Handle timeouts
            await self._handle_timeout_error(e)
            raise
            
        except SerializationError as e:
            # Handle serialization issues
            await self._handle_serialization_error(e)
            raise
            
        except Exception as e:
            # Handle unexpected errors
            raise TransportError(f"Unexpected transport error: {e}")
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreakerTransport(TransportInterface):
    def __init__(self, base_transport: TransportInterface, 
                 failure_threshold: int = 5, 
                 timeout_seconds: int = 60):
        self.base_transport = base_transport
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise TransportError("Circuit breaker is OPEN")
        
        try:
            result = await self.base_transport.send(event, metadata)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        return (time.time() - self.last_failure_time) > self.timeout_seconds
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
base_transport = HTTPTransport("https://unreliable.api.com")
transport = CircuitBreakerTransport(base_transport)

logger = create_with_transport(transport=transport, log_base_dir="./logs")
```

## Performance Considerations

### Connection Pooling

```python
class PooledHTTPTransport(TransportInterface):
    def __init__(self, endpoint_url: str, pool_size: int = 10):
        self.endpoint_url = endpoint_url
        self.pool_size = pool_size
        self.session = None
    
    async def connect(self) -> None:
        connector = aiohttp.TCPConnector(
            limit=self.pool_size,
            limit_per_host=self.pool_size,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=10)
        )
```

### Batching

```python
class BatchingTransport(TransportInterface):
    def __init__(self, base_transport: TransportInterface, 
                 batch_size: int = 10, 
                 flush_interval: float = 5.0):
        self.base_transport = base_transport
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self.batch = []
        self.last_flush = time.time()
        self.lock = asyncio.Lock()
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        async with self.lock:
            self.batch.append((event, metadata))
            
            should_flush = (
                len(self.batch) >= self.batch_size or
                (time.time() - self.last_flush) >= self.flush_interval
            )
            
            if should_flush:
                await self._flush_batch()
        
        return True
    
    async def _flush_batch(self):
        if not self.batch:
            return
        
        batch_to_send = self.batch.copy()
        self.batch.clear()
        self.last_flush = time.time()
        
        # Send batch to base transport
        for event, metadata in batch_to_send:
            await self.base_transport.send(event, metadata)
```

## Testing Transport Implementations

### Mock Transport for Testing

```python
class MockTransport(TransportInterface):
    def __init__(self):
        self.sent_events = []
        self.should_fail = False
        self.call_count = 0
    
    async def send(self, event: Any, metadata: Dict[str, Any] = None) -> bool:
        self.call_count += 1
        
        if self.should_fail:
            raise TransportError("Mock transport failure")
        
        self.sent_events.append({
            'event': event,
            'metadata': metadata,
            'timestamp': time.time()
        })
        
        return True
    
    def reset(self):
        self.sent_events.clear()
        self.call_count = 0
        self.should_fail = False

# Usage in tests
def test_event_transport():
    transport = MockTransport()
    logger = create_with_transport(transport=transport, log_base_dir="./test_logs")
    
    # Test normal operation
    event = TestEvent(session_id="test")
    success = await logger(event)
    
    assert success
    assert len(transport.sent_events) == 1
    assert transport.sent_events[0]['event'] == event
    
    # Test failure handling
    transport.should_fail = True
    success = await logger(event)  # Should still succeed (local logging)
    assert success  # Local logging always succeeds
```

## Best Practices

### 1. Resource Management

- Always implement proper `connect()` and `close()` methods
- Use connection pooling for HTTP/database transports
- Implement async context manager support
- Clean up resources in `close()` method

### 2. Error Handling

- Use specific exception types from `transport_exceptions`
- Implement retry logic for transient failures
- Use circuit breaker pattern for unreliable services
- Log errors with sufficient context

### 3. Performance

- Use connection pooling for network transports
- Implement batching for high-volume scenarios
- Consider async/await patterns throughout
- Monitor and measure transport performance

### 4. Testing

- Create mock implementations for testing
- Test both success and failure scenarios
- Verify resource cleanup
- Test concurrent usage patterns

### 5. Configuration

- Make transports configurable via environment variables
- Support different configurations for dev/staging/production
- Provide sensible defaults
- Document configuration options

## Future Transport Examples

The transport interface is designed to support future integrations:

### Message Queue Integration

```python
# RabbitMQ
transport = RabbitMQTransport(
    connection_url="amqp://localhost",
    exchange="agent_events",
    routing_key="session.events"
)

# Apache Kafka
transport = KafkaTransport(
    bootstrap_servers=["localhost:9092"],
    topic="agent-events"
)

# AWS SQS
transport = SQSTransport(
    queue_url="https://sqs.region.amazonaws.com/account/queue",
    region="us-east-1"
)
```

### Database Integration

```python
# PostgreSQL
transport = PostgreSQLTransport(
    connection_string="postgresql://user:pass@localhost/db",
    table_name="agent_events"
)

# MongoDB
transport = MongoTransport(
    connection_string="mongodb://localhost:27017",
    database="agent_logs",
    collection="events"
)
```

### Cloud Services

```python
# AWS CloudWatch
transport = CloudWatchTransport(
    log_group="/agent-c/events",
    region="us-east-1"
)

# Google Cloud Logging
transport = GCPLoggingTransport(
    project_id="my-project",
    log_name="agent-events"
)
```

The transport interface provides a flexible foundation for integrating with any downstream system while maintaining consistent error handling, resource management, and performance characteristics.