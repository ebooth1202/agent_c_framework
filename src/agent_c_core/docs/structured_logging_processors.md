# Structured Logging Processors

This document describes the core processors in the Agent C structured logging infrastructure. These processors enrich log entries with context, timing, error information, and framework-specific metadata.

## Overview

Processors are functions that transform log entries as they flow through the logging pipeline. Each processor receives a log event dictionary and returns an enhanced version with additional context or formatting.

## Core Processors

### Framework Context Processor (`add_framework_context`)

**Purpose**: Adds framework-wide context and metadata to every log entry.

**Features**:
- Injects context variables (correlation_id, agent_id, session_id, user_id) from contextvars
- Adds framework metadata (framework name, version)
- Preserves explicit values in the event dictionary
- Thread-safe context propagation

**Example**:
```python
# Input
{"event": "user_action", "action": "login"}

# Output (with context)
{
    "event": "user_action",
    "action": "login",
    "correlation_id": "req-123",
    "agent_id": "agent-456",
    "framework": "agent_c",
    "framework_version": "1.0.0"
}
```

### Correlation ID Processor (`add_correlation_id`)

**Purpose**: Ensures correlation ID tracking for request tracing.

**Features**:
- Preserves existing correlation IDs
- Can be extended to generate correlation IDs if missing
- Supports request tracing across service boundaries

### Timing Processor (`add_timing_info`)

**Purpose**: Adds timing information for performance analysis.

**Features**:
- Adds ISO timestamp for human readability
- Includes high-precision nanosecond timestamp for performance analysis
- Preserves existing timing information

**Example**:
```python
# Output
{
    "event": "operation_completed",
    "timestamp": "2023-01-01T12:00:00.123Z",
    "time_ns": 1234567890123456789
}
```

### Error Enrichment Processor (`enrich_errors`)

**Purpose**: Enriches error-level logs with debugging and recovery information.

**Features**:
- Detects error, critical, and exception level logs
- Adds error categorization
- Includes stack traces for exceptions
- Provides context-aware recovery hints
- Only processes error-level logs for performance

**Recovery Hints**:
- Redis connection errors → "Check Redis connection and retry"
- Session not found → "Verify session ID and check expiration"
- Validation errors → "Check input parameters and format"
- Permission errors → "Verify user permissions and authentication"
- Generic errors → "Check logs for more details and retry if transient"

**Example**:
```python
# Input (error level)
{"event": "session_not_found", "session_id": "sess-123"}

# Output
{
    "event": "session_not_found",
    "session_id": "sess-123",
    "error_category": "unknown",
    "recovery_hint": "Verify session ID and check expiration"
}
```

### Agent Context Processor (`add_agent_context`)

**Purpose**: Detects and enriches agent-related events with relevant metadata.

**Features**:
- Detects agent, chat, conversation, and tool events
- Adds component classification
- Categorizes operation types
- Preserves existing component/operation values

**Operation Types**:
- `conversation` - Chat and conversation events
- `tool_usage` - Tool execution events
- `agent_management` - Agent lifecycle events

**Example**:
```python
# Input
{"event": "chat_message_sent", "message_id": "msg-123"}

# Output
{
    "event": "chat_message_sent",
    "message_id": "msg-123",
    "component": "agent",
    "operation_type": "conversation"
}
```

### Sensitive Data Filter (`filter_sensitive_data`)

**Purpose**: Removes or masks sensitive information for security compliance.

**Features**:
- Redacts sensitive field patterns (password, token, key, secret, etc.)
- Masks potential tokens in message content using regex
- Preserves non-sensitive data
- Configurable sensitive patterns

**Sensitive Patterns**:
- Field names: password, token, key, secret, credential, auth, bearer, api_key, access_token
- Message content: Long alphanumeric strings (20+ characters)

**Example**:
```python
# Input
{
    "event": "login_attempt",
    "username": "user123",
    "password": "secret123",
    "message": "Token abc123def456ghi789jkl012mno345pqr678stu901vwx234 received"
}

# Output
{
    "event": "login_attempt",
    "username": "user123",
    "password": "[REDACTED]",
    "message": "Token [TOKEN] received"
}
```

## Default Processor Chain

The `get_default_processors()` function returns the standard processor chain:

1. **Standard structlog processors**:
   - `filter_by_level` - Level-based filtering
   - `add_logger_name` - Logger name injection
   - `add_log_level` - Log level injection
   - `PositionalArgumentsFormatter` - Format positional arguments

2. **Framework processors** (in order):
   - `add_framework_context` - Framework metadata and context
   - `add_correlation_id` - Correlation ID handling
   - `add_timing_info` - Timing information
   - `enrich_errors` - Error enrichment
   - `add_agent_context` - Agent-specific context
   - `filter_sensitive_data` - Security filtering

3. **Final processing**:
   - `StackInfoRenderer` - Stack trace rendering
   - `format_exc_info` - Exception formatting
   - `UnicodeDecoder` - Unicode handling

## Performance Characteristics

All processors are designed for high performance:

- **Target**: < 1ms per processor call
- **Memory**: Minimal memory allocation
- **Thread Safety**: All processors are thread-safe
- **Error Handling**: Processors handle errors gracefully

## Usage Examples

### Basic Usage

```python
from agent_c.util.structured_logging import get_logger
from agent_c.util.structured_logging.context import LoggingContext

# Get a logger with default processors
logger = get_logger(__name__)

# Log with automatic context enrichment
with LoggingContext(correlation_id="req-123", user_id="user-456"):
    logger.info("User action completed", action="login", success=True)
```

### Custom Processor Chain

```python
import structlog
from agent_c.util.structured_logging.processors import (
    add_framework_context,
    add_timing_info,
    filter_sensitive_data
)

# Create custom processor chain
custom_processors = [
    structlog.stdlib.add_log_level,
    add_framework_context,
    add_timing_info,
    filter_sensitive_data,
    structlog.processors.JSONRenderer()
]

# Configure structlog with custom chain
structlog.configure(processors=custom_processors)
```

### Error Logging

```python
try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        operation="risky_operation",
        error_type=type(e).__name__,
        exc_info=True  # Includes stack trace
    )
```

## Testing

Comprehensive unit tests are available in `tests/unit/util/structured_logging/test_processors.py`:

- Individual processor functionality
- Performance benchmarks
- Error handling
- Context injection
- Security filtering

Run tests with:
```bash
python -m pytest tests/unit/util/structured_logging/test_processors.py -v
```

## Extension Points

### Custom Processors

Create custom processors following the standard pattern:

```python
def custom_processor(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Custom processor example."""
    # Add custom logic here
    event_dict['custom_field'] = 'custom_value'
    return event_dict
```

### Project-Specific Processors

Add project-specific processors to the chain:

```python
from agent_c.util.structured_logging.processors import get_default_processors

def get_api_processors():
    """Get processor chain for API project."""
    processors = get_default_processors()
    
    # Insert custom processor before sensitive data filtering
    processors.insert(-3, custom_api_processor)
    
    return processors
```

## Best Practices

1. **Performance**: Keep processors lightweight and fast
2. **Error Handling**: Handle exceptions gracefully within processors
3. **Context**: Use contextvars for automatic context propagation
4. **Security**: Always filter sensitive data before logging
5. **Testing**: Write tests for custom processors
6. **Documentation**: Document custom processor behavior clearly