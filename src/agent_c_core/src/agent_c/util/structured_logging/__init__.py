"""
Structured Logging Infrastructure for Agent C Framework

This package provides a comprehensive structured logging solution using structlog
that maintains backward compatibility with the existing LoggingManager while
adding powerful structured logging capabilities.

Key Features:
- Framework-wide consistent logging
- Automatic context propagation (correlation_id, agent_id, session_id, user_id)
- Backward compatibility with LoggingManager
- Environment-aware configuration (development vs production)
- Rich context binding and structured data
- Performance optimized with minimal overhead

Usage:
    # Simple usage (backward compatible)
    from agent_c.util.structured_logging import get_logger
    logger = get_logger(__name__)
    logger.info("Operation completed", user_id="user-123", operation="create_session")
    
    # Advanced usage with context
    from agent_c.util.structured_logging import LoggingContext
    with LoggingContext(correlation_id="req-456", user_id="user-123"):
        logger.info("Processing request")  # Automatically includes context
        
    # Factory usage for advanced configuration
    from agent_c.util.structured_logging import StructuredLoggerFactory
    factory = StructuredLoggerFactory()
    logger = factory.get_logger(__name__)
"""

from .factory import StructuredLoggerFactory, get_logger
from .context import LoggingContext, get_current_context, clear_context

__all__ = [
    "StructuredLoggerFactory",
    "get_logger", 
    "LoggingContext",
    "get_current_context",
    "clear_context",
]

# Version info
__version__ = "1.0.0"