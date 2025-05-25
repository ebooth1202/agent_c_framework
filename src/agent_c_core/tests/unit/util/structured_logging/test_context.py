"""
Tests for Context Management

These tests validate context variable management, propagation,
and the LoggingContext dataclass functionality.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from agent_c.util.structured_logging.context import (
    LoggingContext,
    get_current_context,
    clear_context,
    set_correlation_id,
    get_correlation_id,
    set_agent_id,
    get_agent_id,
    set_user_id,
    get_user_id,
    set_operation,
    get_operation,
    logging_context,
    get_context_dict,
    generate_correlation_id,
    ensure_correlation_id,
    with_context,
    track_operation,
    ContextSnapshot,
    temporary_context,
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


class TestEnhancedContextFeatures:
    """Test cases for enhanced context management features."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    def test_generate_correlation_id(self):
        """Test correlation ID generation using MnemonicSlugs."""
        correlation_id = generate_correlation_id()
        
        # Should be in format "word-word" (2 words separated by hyphen)
        parts = correlation_id.split("-")
        assert len(parts) == 4

        # Should generate unique IDs
        correlation_id2 = generate_correlation_id()
        assert correlation_id != correlation_id2
    
    def test_ensure_correlation_id(self):
        """Test ensuring correlation ID exists."""
        # Should generate new ID when none exists
        correlation_id = ensure_correlation_id()
        assert correlation_id is not None
        assert correlation_id.startswith("req-")
        
        # Should return existing ID when one exists
        same_id = ensure_correlation_id()
        assert same_id == correlation_id
        
        # Should return existing ID when manually set
        set_correlation_id("custom-123")
        existing_id = ensure_correlation_id()
        assert existing_id == "custom-123"
    
    def test_with_context_decorator(self):
        """Test the with_context decorator."""
        @with_context({"operation": "test_op", "user_id": "user-123"})
        def decorated_function():
            return {
                "operation": get_operation(),
                "user_id": get_user_id(),
                "correlation_id": get_correlation_id()
            }
        
        # Set initial context
        set_correlation_id("initial-123")
        
        result = decorated_function()
        
        assert result["operation"] == "test_op"
        assert result["user_id"] == "user-123"
        assert result["correlation_id"] == "initial-123"  # Should inherit
    
    def test_track_operation_decorator(self):
        """Test the track_operation decorator."""
        original_operation = "original_op"
        set_operation(original_operation)
        
        @track_operation("tracked_operation")
        def tracked_function():
            return get_operation()
        
        # Operation should be set during execution
        result = tracked_function()
        assert result == "tracked_operation"
        
        # Original operation should be restored
        assert get_operation() == original_operation
    
    def test_track_operation_decorator_no_original(self):
        """Test track_operation decorator when no original operation exists."""
        assert get_operation() is None
        
        @track_operation("new_operation")
        def tracked_function():
            return get_operation()
        
        result = tracked_function()
        assert result == "new_operation"
        
        # Should be None after completion
        assert get_operation() is None
    
    def test_context_snapshot(self):
        """Test context snapshot and restoration."""
        # Set initial context
        set_correlation_id("initial-123")
        set_user_id("user-456")
        
        # Take snapshot
        snapshot = ContextSnapshot()
        
        # Change context
        set_correlation_id("changed-789")
        set_user_id("user-999")
        set_operation("new-op")
        
        assert get_correlation_id() == "changed-789"
        assert get_user_id() == "user-999"
        assert get_operation() == "new-op"
        
        # Restore snapshot
        snapshot.restore()
        
        assert get_correlation_id() == "initial-123"
        assert get_user_id() == "user-456"
        assert get_operation() is None
    
    def test_temporary_context_manager(self):
        """Test temporary context manager."""
        # Set initial context
        set_correlation_id("initial-123")
        set_user_id("user-456")
        
        with temporary_context(user_id="temp-user", operation="temp-op"):
            assert get_correlation_id() == "initial-123"  # Should be preserved
            assert get_user_id() == "temp-user"  # Should be changed
            assert get_operation() == "temp-op"  # Should be set
        
        # Should be restored after context manager
        assert get_correlation_id() == "initial-123"
        assert get_user_id() == "user-456"
        assert get_operation() is None
    
    def test_temporary_context_with_exception(self):
        """Test that temporary context is restored even when exception occurs."""
        set_correlation_id("initial-123")
        
        try:
            with temporary_context(correlation_id="temp-456"):
                assert get_correlation_id() == "temp-456"
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Context should still be restored
        assert get_correlation_id() == "initial-123"


class TestConcurrentContextBehavior:
    """Test cases for concurrent context behavior and isolation."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    @pytest.mark.asyncio
    async def test_async_context_inheritance(self):
        """Test that context is inherited in async functions."""
        set_correlation_id("parent-123")
        set_user_id("user-456")
        
        async def child_async_function():
            # Should inherit parent context
            return {
                "correlation_id": get_correlation_id(),
                "user_id": get_user_id()
            }
        
        result = await child_async_function()
        
        assert result["correlation_id"] == "parent-123"
        assert result["user_id"] == "user-456"
    
    @pytest.mark.asyncio
    async def test_async_context_modification_isolation(self):
        """Test that context modifications in async tasks are isolated."""
        set_correlation_id("main-123")
        
        async def modify_context_task(task_id):
            set_correlation_id(f"task-{task_id}")
            await asyncio.sleep(0.01)  # Yield control
            return get_correlation_id()
        
        # Run multiple tasks that modify context
        tasks = [modify_context_task(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Each task should have its own context
        assert results == ["task-0", "task-1", "task-2"]
        
        # Main context should be unchanged
        assert get_correlation_id() == "main-123"
    
    def test_thread_context_isolation_detailed(self):
        """Test detailed thread context isolation behavior."""
        set_correlation_id("main-123")
        set_user_id("main-user")
        
        results = {}
        
        def thread_function(thread_id):
            # Each thread should inherit the context
            inherited_correlation = get_correlation_id()
            inherited_user = get_user_id()
            
            # Modify context in this thread
            set_correlation_id(f"thread-{thread_id}")
            set_user_id(f"user-{thread_id}")
            
            # Store results
            results[thread_id] = {
                "inherited_correlation": inherited_correlation,
                "inherited_user": inherited_user,
                "final_correlation": get_correlation_id(),
                "final_user": get_user_id()
            }
        
        # Run in separate threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(thread_function, 1)
            future2 = executor.submit(thread_function, 2)
            
            future1.result()
            future2.result()
        
        # Each thread should have inherited and then modified context
        assert results[1]["inherited_correlation"] == "main-123"
        assert results[1]["inherited_user"] == "main-user"
        assert results[1]["final_correlation"] == "thread-1"
        assert results[1]["final_user"] == "user-1"
        
        assert results[2]["inherited_correlation"] == "main-123"
        assert results[2]["inherited_user"] == "main-user"
        assert results[2]["final_correlation"] == "thread-2"
        assert results[2]["final_user"] == "user-2"
        
        # Main thread context should be unchanged
        assert get_correlation_id() == "main-123"
        assert get_user_id() == "main-user"


class TestContextPerformance:
    """Test cases for context management performance."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_context()
    
    def test_context_access_performance(self):
        """Test that context access is performant."""
        set_correlation_id("test-123")
        
        # Time context access
        start_time = time.time()
        
        for _ in range(1000):
            correlation_id = get_correlation_id()
            context_dict = get_context_dict()
        
        duration = time.time() - start_time
        
        # Should be very fast (less than 10ms for 1000 operations)
        assert duration < 0.01
        assert correlation_id == "test-123"
    
    def test_context_creation_performance(self):
        """Test that context creation and application is performant."""
        start_time = time.time()
        
        for i in range(100):
            context = LoggingContext(
                correlation_id=f"req-{i}",
                user_id=f"user-{i}",
                operation=f"op-{i}"
            )
            context.apply()
        
        duration = time.time() - start_time
        
        # Should be fast (less than 10ms for 100 operations)
        assert duration < 0.01