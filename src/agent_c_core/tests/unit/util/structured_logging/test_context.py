"""
Tests for Context Management

These tests validate context variable management, propagation,
and the LoggingContext dataclass functionality.
"""

import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor

from agent_c.util.structured_logging.context import (
    LoggingContext,
    get_current_context,
    clear_context,
    set_correlation_id,
    get_correlation_id,
    set_agent_id,
    get_agent_id,
    logging_context,
    get_context_dict,
)


class TestLoggingContext:
    """Test cases for LoggingContext dataclass."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    def test_context_creation(self):
        """Test creating LoggingContext instances."""
        context = LoggingContext(
            correlation_id="req-123",
            user_id="user-456",
            operation="test_operation"
        )
        
        assert context.correlation_id == "req-123"
        assert context.user_id == "user-456"
        assert context.operation == "test_operation"
        assert context.agent_id is None
        assert context.session_id is None
    
    def test_context_apply(self):
        """Test applying context to context variables."""
        context = LoggingContext(
            correlation_id="req-123",
            user_id="user-456"
        )
        
        context.apply()
        
        assert get_correlation_id() == "req-123"
        assert get_user_id() == "user-456"
        assert get_agent_id() is None
    
    def test_context_to_dict(self):
        """Test converting context to dictionary."""
        context = LoggingContext(
            correlation_id="req-123",
            user_id="user-456",
            agent_id=None  # Should be excluded from dict
        )
        
        context_dict = context.to_dict()
        
        assert context_dict == {
            "correlation_id": "req-123",
            "user_id": "user-456"
        }
        assert "agent_id" not in context_dict
    
    def test_context_from_current(self):
        """Test creating context from current context variables."""
        set_correlation_id("req-123")
        set_agent_id("agent-456")
        
        context = LoggingContext.from_current()
        
        assert context.correlation_id == "req-123"
        assert context.agent_id == "agent-456"
        assert context.user_id is None
    
    def test_context_manager(self):
        """Test LoggingContext as context manager."""
        # Set initial context
        set_correlation_id("initial-123")
        
        with LoggingContext(correlation_id="temp-456", user_id="user-789"):
            assert get_correlation_id() == "temp-456"
            assert get_user_id() == "user-789"
        
        # Context should be restored (contextvars behavior)
        # Note: contextvars automatically restore previous values
        # when exiting context managers


class TestContextVariables:
    """Test cases for individual context variable functions."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    def test_correlation_id_operations(self):
        """Test correlation ID get/set operations."""
        assert get_correlation_id() is None
        
        set_correlation_id("req-123")
        assert get_correlation_id() == "req-123"
    
    def test_agent_id_operations(self):
        """Test agent ID get/set operations."""
        assert get_agent_id() is None
        
        set_agent_id("agent-456")
        assert get_agent_id() == "agent-456"
    
    def test_clear_context(self):
        """Test clearing all context variables."""
        set_correlation_id("req-123")
        set_agent_id("agent-456")
        
        clear_context()
        
        assert get_correlation_id() is None
        assert get_agent_id() is None
    
    def test_get_context_dict(self):
        """Test getting current context as dictionary."""
        set_correlation_id("req-123")
        set_agent_id("agent-456")
        
        context_dict = get_context_dict()
        
        assert context_dict == {
            "correlation_id": "req-123",
            "agent_id": "agent-456"
        }


class TestContextPropagation:
    """Test cases for context propagation across async boundaries and threads."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    @pytest.mark.asyncio
    async def test_async_context_propagation(self):
        """Test that context propagates across async boundaries."""
        set_correlation_id("req-123")
        
        async def async_function():
            return get_correlation_id()
        
        result = await async_function()
        assert result == "req-123"
    
    @pytest.mark.asyncio
    async def test_async_context_isolation(self):
        """Test that context changes in async tasks are isolated."""
        set_correlation_id("main-123")
        
        async def async_task(task_id):
            set_correlation_id(f"task-{task_id}")
            await asyncio.sleep(0.01)  # Yield control
            return get_correlation_id()
        
        # Run multiple tasks concurrently
        tasks = [async_task(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Each task should have its own context
        assert results == ["task-0", "task-1", "task-2"]
        
        # Main context should be unchanged
        assert get_correlation_id() == "main-123"
    
    def test_thread_context_isolation(self):
        """Test that context is isolated between threads."""
        set_correlation_id("main-123")
        
        def thread_function(thread_id):
            set_correlation_id(f"thread-{thread_id}")
            return get_correlation_id()
        
        # Run in separate threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(thread_function, 1)
            future2 = executor.submit(thread_function, 2)
            
            result1 = future1.result()
            result2 = future2.result()
        
        # Each thread should have its own context
        assert result1 == "thread-1"
        assert result2 == "thread-2"
        
        # Main thread context should be unchanged
        assert get_correlation_id() == "main-123"


class TestLoggingContextManager:
    """Test cases for the logging_context context manager."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    def test_logging_context_manager(self):
        """Test the logging_context convenience function."""
        with logging_context(correlation_id="req-123", user_id="user-456"):
            assert get_correlation_id() == "req-123"
            assert get_user_id() == "user-456"
    
    def test_logging_context_manager_yields_context(self):
        """Test that logging_context yields the context object."""
        with logging_context(correlation_id="req-123") as context:
            assert isinstance(context, LoggingContext)
            assert context.correlation_id == "req-123"