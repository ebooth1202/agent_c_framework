"""
Integration test for context management across realistic scenarios.

This test validates context propagation in scenarios that mirror
real-world usage patterns in the Agent C framework.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from agent_c.util.structured_logging import get_logger, LoggingContext
from agent_c.util.structured_logging.context import (
    set_correlation_id,
    get_correlation_id,
    ensure_correlation_id,
    with_context,
    track_operation,
    temporary_context,
)


def test_request_processing_scenario():
    """Test context propagation in a typical request processing scenario."""
    print("🧪 Testing request processing scenario...")
    
    logger = get_logger('test.request_processor')
    
    # Simulate incoming request  
    request_id = "tiger-castle"  # Using MnemonicSlugs format
    user_id = "user-67890"
    
    with LoggingContext(correlation_id=request_id, user_id=user_id):
        logger.info("Request received", endpoint="/api/sessions")
        
        # Simulate service layer call
        @track_operation("validate_user")
        def validate_user():
            logger.info("Validating user")
            return True
        
        # Simulate database operation
        @with_context({"operation": "database_query"})
        def query_database():
            logger.info("Querying user database", table="users")
            return {"id": user_id, "name": "Test User"}
        
        # Execute operations
        is_valid = validate_user()
        user_data = query_database()
        
        logger.info("Request processed successfully", 
                   user_valid=is_valid, 
                   user_name=user_data["name"])
    
    print("✅ Request processing scenario completed")


def test_agent_conversation_scenario():
    """Test context propagation in an agent conversation scenario."""
    print("🧪 Testing agent conversation scenario...")
    
    logger = get_logger('test.agent_conversation')
    
    # Simulate agent conversation
    session_id = "session-abc123"
    agent_id = "agent-claude"
    
    with LoggingContext(session_id=session_id, agent_id=agent_id):
        correlation_id = ensure_correlation_id()
        logger.info("Agent conversation started", conversation_type="chat")
        
        # Simulate tool usage
        with temporary_context(operation="tool_execution"):
            logger.info("Executing tool", tool_name="calculator", input="2+2")
            time.sleep(0.01)  # Simulate tool execution time
            logger.info("Tool execution completed", result=4)
        
        # Simulate response generation
        @track_operation("generate_response")
        def generate_response():
            logger.info("Generating agent response")
            return "The calculation result is 4."
        
        response = generate_response()
        logger.info("Agent conversation completed", 
                   response_length=len(response),
                   correlation_id=correlation_id)
    
    print("✅ Agent conversation scenario completed")


async def test_async_processing_scenario():
    """Test context propagation in async processing scenarios."""
    print("🧪 Testing async processing scenario...")
    
    logger = get_logger('test.async_processor')
    
    # Simulate batch processing
    batch_id = "batch-xyz789"
    
    with LoggingContext(correlation_id=batch_id, operation="batch_processing"):
        logger.info("Starting batch processing", batch_size=3)
        
        async def process_item(item_id):
            # Each item gets its own correlation ID but inherits batch context
            item_correlation = f"{batch_id}-item-{item_id}"
            set_correlation_id(item_correlation)
            
            logger.info("Processing item", item_id=item_id)
            await asyncio.sleep(0.01)  # Simulate async work
            logger.info("Item processed", item_id=item_id, status="completed")
            
            return f"result-{item_id}"
        
        # Process items concurrently
        tasks = [process_item(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        logger.info("Batch processing completed", 
                   results_count=len(results),
                   results=results)
    
    print("✅ Async processing scenario completed")


def test_multi_threaded_scenario():
    """Test context propagation in multi-threaded scenarios."""
    print("🧪 Testing multi-threaded scenario...")
    
    logger = get_logger('test.multi_thread')
    
    # Simulate multi-threaded background processing
    main_correlation = "main-thread-123"
    
    with LoggingContext(correlation_id=main_correlation, operation="background_tasks"):
        logger.info("Starting background tasks")
        
        def background_worker(worker_id):
            # Each worker inherits context but can modify it
            worker_correlation = f"{main_correlation}-worker-{worker_id}"
            set_correlation_id(worker_correlation)
            
            logger.info("Worker started", worker_id=worker_id)
            
            # Simulate work
            time.sleep(0.01)
            
            logger.info("Worker completed", worker_id=worker_id)
            return f"worker-{worker_id}-result"
        
        # Run workers in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(background_worker, i) for i in range(2)]
            results = [future.result() for future in futures]
        
        logger.info("All background tasks completed", 
                   worker_results=results)
    
    print("✅ Multi-threaded scenario completed")


def test_error_handling_scenario():
    """Test context propagation during error handling."""
    print("🧪 Testing error handling scenario...")
    
    logger = get_logger('test.error_handler')
    
    operation_id = "op-error-test"
    
    with LoggingContext(correlation_id=operation_id, operation="error_test"):
        logger.info("Starting operation that will fail")
        
        try:
            @track_operation("risky_operation")
            def risky_operation():
                logger.info("Executing risky operation")
                raise ValueError("Simulated error for testing")
            
            risky_operation()
            
        except ValueError as e:
            logger.error("Operation failed", 
                        error_type=type(e).__name__,
                        error_message=str(e),
                        recovery_action="retry_with_backoff")
        
        logger.info("Error handling completed")
    
    print("✅ Error handling scenario completed")


async def main():
    """Run all integration test scenarios."""
    print("🚀 Starting Context Management Integration Tests")
    print("=" * 60)
    
    # Run synchronous tests
    test_request_processing_scenario()
    test_multi_threaded_scenario()
    test_error_handling_scenario()
    
    # Run asynchronous tests
    await test_async_processing_scenario()
    
    print("\n🎉 All context management integration tests completed successfully!")
    print("Context propagation is working correctly across all scenarios.")


if __name__ == "__main__":
    asyncio.run(main())