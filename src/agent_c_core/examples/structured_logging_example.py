"""
Example demonstrating structured logging usage in Agent C framework.

This example shows how to use the new structured logging infrastructure
with various patterns and features.
"""

import time
from agent_c.util.structured_logging import get_logger, LoggingContext


def main():
    """Demonstrate structured logging features."""
    print("🚀 Agent C Structured Logging Example")
    print("=" * 50)
    
    # Get a logger (works like LoggingManager)
    logger = get_logger(__name__)
    
    print("\n1. Basic structured logging:")
    logger.info("Application started", version="1.0.0", component="example")
    
    print("\n2. Logging with context:")
    with LoggingContext(correlation_id="req-123", user_id="user-456"):
        logger.info("Processing user request", operation="get_profile")
        logger.info("Database query executed", table="users", duration_ms=25)
    
    print("\n3. Error logging with context:")
    try:
        # Simulate an error
        raise ValueError("Example error for demonstration")
    except Exception as e:
        logger.error("Operation failed", 
                    operation="example_operation",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    recovery_hint="Check input parameters")
    
    print("\n4. Performance logging:")
    start_time = time.time()
    time.sleep(0.1)  # Simulate work
    duration = time.time() - start_time
    
    logger.info("Operation completed",
               operation="example_work",
               duration_seconds=duration,
               status="success")
    
    print("\n5. Agent-specific logging:")
    with LoggingContext(agent_id="agent-789", session_id="session-abc"):
        logger.info("Agent conversation started",
                   agent_type="claude",
                   conversation_id="conv-123")
        
        logger.info("Tool execution",
                   tool_name="calculator",
                   tool_input={"operation": "add", "a": 5, "b": 3},
                   tool_output=8)
    
    print("\n✅ Example completed successfully!")
    print("Check the log output above to see structured logging in action.")


if __name__ == "__main__":
    main()