# EventSessionLogger API Design Specification

## Overview

The EventSessionLogger implements a **gateway pattern** that acts as a bridge between agent events and transport layers. It provides local logging with optional downstream forwarding, enabling future decoupling to queues, message buses, or other transport mechanisms.

## Core Design Principles

1. **Gateway Pattern**: Acts as man-in-the-middle between agents and transport
2. **Error Isolation**: Local logging never fails due to transport issues
3. **Dual Interface**: Supports both callback and transport downstream patterns
4. **Backward Compatibility**: Maintains current SessionLogger behavior and configuration
5. **Future Ready**: Designed for easy transport layer swapping

## EventSessionLogger Class API

### Constructor

```python
class EventSessionLogger:
    def __init__(
        self,
        log_base_dir: Union[str, Path] = None,
        downstream_callback: Optional[Callable[[Any], Awaitable[None]]] = None,
        downstream_transport: Optional['TransportInterface'] = None,
        include_system_prompt: bool = True,
        log_format: str = "jsonl",
        file_naming_pattern: str = "%Y%m%d_%H%M%S",
        error_handler: Optional[Callable[[Exception, str], None]] = None,
        max_retry_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
        enable_local_logging: bool = True,
        session_directory_pattern: str = "{session_id}",
        unknown_session_pattern: str = "unknown_{uuid}",
        **kwargs
    ) -> None:
```

**Parameters:**
- `log_base_dir`: Base directory for logs (default: from AGENT_LOG_DIR env var or "logs/sessions")
- `downstream_callback`: Optional callback for current transition pattern
- `downstream_transport`: Optional transport interface for future decoupling
- `include_system_prompt`: Whether to log system prompts (backward compatibility)
- `log_format`: Log format ("jsonl", "json", "custom")
- `file_naming_pattern`: strftime pattern for log files
- `error_handler`: Custom error handling callback
- `max_retry_attempts`: Maximum retries for downstream operations
- `retry_delay_seconds`: Delay between retry attempts
- `enable_local_logging`: Whether to perform local logging (always True by default)
- `session_directory_pattern`: Pattern for session directories
- `unknown_session_pattern`: Pattern for unknown session directories

### Core Gateway Method

```python
async def __call__(self, event: Any) -> bool:
    """
    Main gateway method - processes events through the logging pipeline.
    
    Always logs locally first, then forwards to downstream if configured.
    Error isolation ensures local logging success doesn't depend on transport.
    
    Args:
        event: Event object (SessionEvent, SemiSessionEvent, or any serializable object)
        
    Returns:
        bool: True if local logging succeeded (transport failures don't affect return value)
        
    Raises:
        EventSessionLoggerError: Only for critical local logging failures
    """
```

### Configuration Methods

```python
def configure_from_env(self) -> None:
    """Load configuration from environment variables"""

def update_downstream_callback(self, callback: Optional[Callable]) -> None:
    """Update downstream callback (for runtime reconfiguration)"""

def update_downstream_transport(self, transport: Optional['TransportInterface']) -> None:
    """Update downstream transport (for runtime reconfiguration)"""

def get_log_file_path(self, session_id: str) -> Path:
    """Get the current log file path for a session"""

def get_session_directory(self, session_id: str) -> Path:
    """Get the session directory path"""
```

### Resource Management

```python
async def close(self) -> None:
    """Clean shutdown - close transport connections and flush logs"""

async def __aenter__(self) -> 'EventSessionLogger':
    """Async context manager entry"""

async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
    """Async context manager exit with cleanup"""
```

## TransportInterface Abstract Class

```python
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

class TransportInterface(ABC):
    """
    Abstract interface for transport layers in the EventSessionLogger gateway pattern.
    
    Implementations can include:
    - Queue-based transports (RabbitMQ, Redis, AWS SQS)
    - Message bus transports (Kafka, Azure Service Bus)
    - HTTP-based transports (webhooks, REST APIs)
    - Custom application-specific transports
    """
    
    @abstractmethod
    async def send(self, event: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send an event through the transport layer.
        
        Args:
            event: Serialized event data
            metadata: Optional routing/transport metadata
            
        Returns:
            bool: True if send succeeded, False otherwise
            
        Raises:
            TransportError: For transport-specific failures
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean shutdown of transport connections"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if transport is healthy and ready"""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if transport is currently connected"""
        pass
```

## Error Handling Strategy

### Exception Hierarchy

```python
class EventSessionLoggerError(Exception):
    """Base exception for EventSessionLogger"""
    pass

class LocalLoggingError(EventSessionLoggerError):
    """Raised when local logging fails"""
    pass

class TransportError(EventSessionLoggerError):
    """Base exception for transport-related errors"""
    pass

class TransportConnectionError(TransportError):
    """Raised when transport connection fails"""
    pass

class TransportTimeoutError(TransportError):
    """Raised when transport operations timeout"""
    pass

class SerializationError(EventSessionLoggerError):
    """Raised when event serialization fails"""
    pass
```

### Error Isolation Pattern

```python
async def __call__(self, event: Any) -> bool:
    """Gateway method with error isolation"""
    local_success = False
    transport_success = False
    
    # PHASE 1: Local logging (never fails due to transport issues)
    try:
        local_success = await self._log_locally(event)
    except Exception as e:
        self._handle_local_error(e, event)
        raise LocalLoggingError(f"Local logging failed: {e}")
    
    # PHASE 2: Downstream forwarding (isolated from local logging)
    if self.downstream_callback or self.downstream_transport:
        try:
            transport_success = await self._forward_downstream(event)
        except Exception as e:
            # Transport errors are logged but don't affect local logging success
            self._handle_transport_error(e, event)
    
    return local_success  # Success based only on local logging
```

### Graceful Degradation

```python
async def _forward_downstream(self, event: Any) -> bool:
    """Forward to downstream with graceful degradation"""
    
    # Try callback first (current transition pattern)
    if self.downstream_callback:
        try:
            await self._retry_operation(
                lambda: self.downstream_callback(event),
                "downstream_callback"
            )
            return True
        except Exception as e:
            self._log_transport_error("callback", e, event)
    
    # Try transport second (future pattern)
    if self.downstream_transport:
        try:
            await self._retry_operation(
                lambda: self.downstream_transport.send(event),
                "downstream_transport"
            )
            return True
        except Exception as e:
            self._log_transport_error("transport", e, event)
    
    return False
```

## Configuration System

### Environment Variables

```python
# Supported environment variables (backward compatible)
AGENT_LOG_DIR = "logs/sessions"           # Base log directory
AGENT_LOG_FORMAT = "jsonl"                # Log format
AGENT_LOG_INCLUDE_PROMPT = "true"         # Include system prompts
AGENT_LOG_MAX_RETRIES = "3"               # Max retry attempts
AGENT_LOG_RETRY_DELAY = "1.0"             # Retry delay seconds
AGENT_LOG_FILE_PATTERN = "%Y%m%d_%H%M%S"  # File naming pattern
AGENT_LOG_ENABLE_LOCAL = "true"           # Enable local logging
AGENT_LOG_SESSION_PATTERN = "{session_id}" # Session directory pattern
```

### Configuration Loading

```python
def _load_configuration(self) -> Dict[str, Any]:
    """Load configuration from environment variables with defaults"""
    return {
        'log_base_dir': os.getenv('AGENT_LOG_DIR', 'logs/sessions'),
        'log_format': os.getenv('AGENT_LOG_FORMAT', 'jsonl'),
        'include_system_prompt': os.getenv('AGENT_LOG_INCLUDE_PROMPT', 'true').lower() == 'true',
        'max_retry_attempts': int(os.getenv('AGENT_LOG_MAX_RETRIES', '3')),
        'retry_delay_seconds': float(os.getenv('AGENT_LOG_RETRY_DELAY', '1.0')),
        'file_naming_pattern': os.getenv('AGENT_LOG_FILE_PATTERN', '%Y%m%d_%H%M%S'),
        'enable_local_logging': os.getenv('AGENT_LOG_ENABLE_LOCAL', 'true').lower() == 'true',
        'session_directory_pattern': os.getenv('AGENT_LOG_SESSION_PATTERN', '{session_id}'),
        'unknown_session_pattern': os.getenv('AGENT_LOG_UNKNOWN_PATTERN', 'unknown_{uuid}')
    }
```

## Factory Functions

### Basic Factory Functions

```python
def create_session_logger(
    log_base_dir: Optional[str] = None,
    downstream_callback: Optional[Callable] = None,
    **kwargs
) -> EventSessionLogger:
    """
    Create EventSessionLogger with basic configuration.
    
    Args:
        log_base_dir: Base directory for logs
        downstream_callback: Optional callback for transition
        **kwargs: Additional configuration options
        
    Returns:
        Configured EventSessionLogger instance
    """
    config = _load_default_config()
    if log_base_dir:
        config['log_base_dir'] = log_base_dir
    if downstream_callback:
        config['downstream_callback'] = downstream_callback
    config.update(kwargs)
    
    return EventSessionLogger(**config)

def create_logging_only(
    log_base_dir: Optional[str] = None,
    **kwargs
) -> EventSessionLogger:
    """
    Create EventSessionLogger for local logging only (no downstream).
    
    Useful for:
    - Development and testing
    - Simple logging scenarios
    - Migration testing
    """
    return create_session_logger(
        log_base_dir=log_base_dir,
        downstream_callback=None,
        downstream_transport=None,
        **kwargs
    )

def create_with_callback(
    callback: Callable,
    log_base_dir: Optional[str] = None,
    **kwargs
) -> EventSessionLogger:
    """
    Create EventSessionLogger with downstream callback (transition pattern).
    
    Args:
        callback: Downstream callback function
        log_base_dir: Base directory for logs
        **kwargs: Additional configuration options
    """
    return create_session_logger(
        log_base_dir=log_base_dir,
        downstream_callback=callback,
        **kwargs
    )

def create_with_transport(
    transport: TransportInterface,
    log_base_dir: Optional[str] = None,
    **kwargs
) -> EventSessionLogger:
    """
    Create EventSessionLogger with transport layer (future pattern).
    
    Args:
        transport: Transport interface implementation
        log_base_dir: Base directory for logs
        **kwargs: Additional configuration options
    """
    return create_session_logger(
        log_base_dir=log_base_dir,
        downstream_transport=transport,
        **kwargs
    )
```

### Environment-Based Factory

```python
def create_from_environment(**overrides) -> EventSessionLogger:
    """
    Create EventSessionLogger from environment variables.
    
    Args:
        **overrides: Override specific configuration values
        
    Returns:
        EventSessionLogger configured from environment
    """
    config = _load_configuration()
    config.update(overrides)
    return EventSessionLogger(**config)
```

### Migration Utilities

```python
def migrate_from_session_logger(
    old_session_logger: 'SessionLogger',
    downstream_callback: Optional[Callable] = None
) -> EventSessionLogger:
    """
    Create EventSessionLogger with configuration migrated from old SessionLogger.
    
    Args:
        old_session_logger: Existing SessionLogger instance
        downstream_callback: Optional downstream callback
        
    Returns:
        EventSessionLogger with migrated configuration
    """
    # Extract configuration from old SessionLogger
    log_base_dir = str(old_session_logger.log_file_path.parent.parent)
    include_system_prompt = old_session_logger.include_system_prompt
    
    return create_session_logger(
        log_base_dir=log_base_dir,
        include_system_prompt=include_system_prompt,
        downstream_callback=downstream_callback
    )

def create_backward_compatible(**kwargs) -> EventSessionLogger:
    """
    Create EventSessionLogger with maximum backward compatibility.
    
    Maintains all current SessionLogger behavior while adding gateway capabilities.
    """
    return create_session_logger(
        log_format="jsonl",  # Match current format
        file_naming_pattern="%Y%m%d_%H%M%S",  # Match current naming
        include_system_prompt=True,  # Match current default
        enable_local_logging=True,  # Always enable
        **kwargs
    )
```

## Example Transport Implementations

### CallbackTransport (Transition Helper)

```python
class CallbackTransport(TransportInterface):
    """Transport wrapper for callback functions (transition helper)"""
    
    def __init__(self, callback: Callable[[Any], Awaitable[None]]):
        self.callback = callback
        self._connected = True
    
    async def send(self, event: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            await self.callback(event)
            return True
        except Exception:
            return False
    
    async def close(self) -> None:
        self._connected = False
    
    async def health_check(self) -> bool:
        return self._connected
    
    @property
    def is_connected(self) -> bool:
        return self._connected
```

### LoggingTransport (Development/Testing)

```python
class LoggingTransport(TransportInterface):
    """Transport that logs events to standard logging (for development/testing)"""
    
    def __init__(self, logger_name: str = "event_transport"):
        self.logger = logging.getLogger(logger_name)
        self._connected = True
    
    async def send(self, event: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            event_data = event.model_dump() if hasattr(event, 'model_dump') else str(event)
            self.logger.info(f"Transport event: {event_data}")
            return True
        except Exception as e:
            self.logger.error(f"Transport error: {e}")
            return False
    
    async def close(self) -> None:
        self._connected = False
    
    async def health_check(self) -> bool:
        return self._connected
    
    @property
    def is_connected(self) -> bool:
        return self._connected
```

### NullTransport (Testing)

```python
class NullTransport(TransportInterface):
    """No-op transport for testing"""
    
    def __init__(self):
        self._connected = True
    
    async def send(self, event: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always succeeds
    
    async def close(self) -> None:
        self._connected = False
    
    async def health_check(self) -> bool:
        return self._connected
    
    @property
    def is_connected(self) -> bool:
        return self._connected
```

## Usage Examples

### Basic Gateway Usage

```python
# Simple local logging only
logger = create_logging_only(log_base_dir="./logs")
await logger(event)

# With downstream callback (transition pattern)
async def my_callback(event):
    print(f"Received event: {event.type}")

logger = create_with_callback(my_callback, log_base_dir="./logs")
await logger(event)

# With transport (future pattern)
transport = MyQueueTransport(connection_string="...")
logger = create_with_transport(transport, log_base_dir="./logs")
await logger(event)
```

### Environment-Based Configuration

```python
# Set environment variables
os.environ['AGENT_LOG_DIR'] = '/var/log/agent'
os.environ['AGENT_LOG_MAX_RETRIES'] = '5'

# Create from environment
logger = create_from_environment()
await logger(event)
```

### Migration from Old SessionLogger

```python
# Old pattern
old_logger = SessionLogger("/path/to/logs/session.jsonl")
old_logger.log_event(event)

# New pattern (backward compatible)
new_logger = create_backward_compatible(
    log_base_dir="/path/to/logs",
    downstream_callback=my_app_callback
)
await new_logger(event)
```

### Async Context Manager

```python
async with create_session_logger(downstream_callback=callback) as logger:
    await logger(event1)
    await logger(event2)
    # Automatic cleanup on exit
```

## Performance Considerations

### Memory Efficiency
- **Streaming processing** - events are processed one at a time
- **No event buffering** - immediate processing reduces memory usage
- **Lazy file creation** - log files created only when needed
- **Resource cleanup** - proper async context manager support

### Error Recovery
- **Retry mechanisms** - configurable retry attempts with exponential backoff
- **Circuit breaker pattern** - disable failing transports temporarily
- **Health checks** - monitor transport health and recover automatically
- **Graceful degradation** - continue local logging even if transport fails

### Monitoring and Observability
- **Error metrics** - track local vs transport error rates
- **Performance metrics** - measure gateway overhead vs direct logging
- **Health metrics** - monitor transport connection status
- **Custom error handlers** - integrate with monitoring systems

## Migration Compatibility

### Backward Compatibility Guarantees
- ✅ **File format** - maintains JSON Lines format
- ✅ **Directory structure** - preserves session-based organization
- ✅ **Environment variables** - supports existing AGENT_LOG_DIR
- ✅ **File naming** - maintains timestamp-based naming pattern
- ✅ **Configuration** - supports all current SessionLogger options

### Breaking Changes (None)
- **No API changes** for existing SessionLogger users
- **No file format changes** - existing logs remain readable
- **No configuration changes** - existing environment variables work
- **No behavior changes** - logging behavior is preserved

---

## API Design Summary

**✅ Complete EventSessionLogger API specification**
- Gateway pattern with dual interface support (callback + transport)
- Comprehensive error isolation and handling
- Full backward compatibility with current SessionLogger
- Environment-based configuration with migration support
- Factory functions for common usage patterns
- Abstract transport interface for future extensibility
- Example transport implementations for development/testing

**✅ Ready for implementation** - All API components defined with clear interfaces, error handling, and usage patterns.

**Next Phase:** Implementation of the EventSessionLogger gateway pattern based on this specification.