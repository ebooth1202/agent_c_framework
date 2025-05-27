"""
Tests for Testing Infrastructure

These tests validate the testing utilities, fixtures, and assertion helpers
for structured logging validation.
"""

import pytest
import time
import threading
from unittest.mock import patch

from agent_c.util.structured_logging.testing import (
    LogEntry,
    StructuredLogCapture,
    MockStructuredLogger,
    PerformanceTester,
    PerformanceMetrics,
    LoggingTestPatterns,
    create_test_context,
    assert_log_performance,
    capture_logs_for_function,
    temporary_log_capture,
    mock_structured_logger,
    performance_test,
    with_log_capture,
    with_isolated_context,
)
from agent_c.util.structured_logging.context import LoggingContext, clear_context, get_current_context
from agent_c.util.structured_logging.factory import get_logger


class TestLogEntry:
    """Test cases for LogEntry dataclass."""
    
    def test_log_entry_creation(self):
        """Test creating LogEntry instances."""
        entry = LogEntry(
            level="info",
            message="Test message",
            context={"user_id": "123", "operation": "test"},
        )
        
        assert entry.level == "info"
        assert entry.message == "Test message"
        assert entry.context["user_id"] == "123"
        assert entry.context["operation"] == "test"
        assert entry.timestamp is not None
    
    def test_has_context(self):
        """Test context checking functionality."""
        entry = LogEntry(
            level="info",
            message="Test message",
            context={"user_id": "123", "operation": "test", "status": "success"},
        )
        
        # Test exact matches
        assert entry.has_context(user_id="123")
        assert entry.has_context(operation="test")
        assert entry.has_context(user_id="123", operation="test")
        
        # Test mismatches
        assert not entry.has_context(user_id="456")
        assert not entry.has_context(missing_key="value")
        assert not entry.has_context(user_id="123", operation="wrong")
    
    def test_matches_pattern(self):
        """Test pattern matching functionality."""
        entry = LogEntry(
            level="warning",
            message="Operation failed for user",
            context={"user_id": "123", "error_code": "404"},
        )
        
        # Test message pattern matching
        assert entry.matches_pattern(message_pattern="Operation failed")
        assert entry.matches_pattern(message_pattern="failed for user")
        assert not entry.matches_pattern(message_pattern="success")
        
        # Test level matching
        assert entry.matches_pattern(level="warning")
        assert entry.matches_pattern(level="WARNING")  # Case insensitive
        assert not entry.matches_pattern(level="error")
        
        # Test context pattern matching
        assert entry.matches_pattern(user_id="123")
        assert entry.matches_pattern(error_code="404")
        assert entry.matches_pattern(user_id="123", error_code="404")
        assert not entry.matches_pattern(user_id="456")
        
        # Test combined patterns
        assert entry.matches_pattern(
            message_pattern="failed",
            level="warning",
            user_id="123"
        )
        assert not entry.matches_pattern(
            message_pattern="success",
            level="warning",
            user_id="123"
        )


class TestStructuredLogCapture:
    """Test cases for StructuredLogCapture."""
    
    def test_basic_capture(self):
        """Test basic log capture functionality."""
        capture = StructuredLogCapture()
        capture.start_capture()
        
        try:
            # Add a log entry using the manual method
            capture.add_log_entry('info', 'Test message', user_id='123')
            
            assert len(capture.entries) == 1
            entry = capture.entries[0]
            assert entry.level == "INFO"
            assert entry.message == "Test message"
            assert entry.context["user_id"] == "123"
        finally:
            capture.stop_capture()
    
    def test_get_entries_filtering(self):
        """Test filtering of captured entries."""
        capture = StructuredLogCapture()
        
        # Add test entries
        capture.entries = [
            LogEntry("info", "User login", {"user_id": "123", "action": "login"}),
            LogEntry("warning", "Failed attempt", {"user_id": "123", "action": "login"}),
            LogEntry("info", "User logout", {"user_id": "123", "action": "logout"}),
            LogEntry("error", "System error", {"component": "database"}),
        ]
        
        # Test level filtering
        info_entries = capture.get_entries(level="info")
        assert len(info_entries) == 2
        assert all(e.level == "info" for e in info_entries)
        
        # Test message pattern filtering
        login_entries = capture.get_entries(message_pattern="login")
        assert len(login_entries) == 1
        assert "User login" in login_entries[0].message
        
        # Test context filtering
        user_entries = capture.get_entries(user_id="123")
        assert len(user_entries) == 3
        assert all(e.context.get("user_id") == "123" for e in user_entries)
        
        # Test combined filtering
        user_info_entries = capture.get_entries(level="info", user_id="123")
        assert len(user_info_entries) == 2
    
    def test_assert_logged(self):
        """Test log assertion functionality."""
        capture = StructuredLogCapture()
        
        # Add test entries
        capture.entries = [
            LogEntry("info", "Operation completed", {"user_id": "123", "operation": "create"}),
            LogEntry("warning", "Rate limit exceeded", {"user_id": "456"}),
        ]
        
        # Test successful assertions
        capture.assert_logged("Operation completed", level="info")
        capture.assert_logged(level="warning", user_id="456")
        capture.assert_logged("completed", user_id="123", operation="create")
        
        # Test count assertions
        capture.assert_logged(count=1, level="info")
        capture.assert_logged(count=2)  # Total entries
        
        # Test failed assertions
        with pytest.raises(AssertionError):
            capture.assert_logged("Nonexistent message")
        
        with pytest.raises(AssertionError):
            capture.assert_logged(level="error")
        
        with pytest.raises(AssertionError):
            capture.assert_logged(count=5)
    
    def test_assert_not_logged(self):
        """Test negative log assertion functionality."""
        capture = StructuredLogCapture()
        
        # Add test entries
        capture.entries = [
            LogEntry("info", "Operation completed", {"user_id": "123"}),
        ]
        
        # Test successful negative assertions
        capture.assert_not_logged("Nonexistent message")
        capture.assert_not_logged(level="error")
        capture.assert_not_logged(user_id="456")
        
        # Test failed negative assertions
        with pytest.raises(AssertionError):
            capture.assert_not_logged("Operation completed")
        
        with pytest.raises(AssertionError):
            capture.assert_not_logged(level="info")
    
    def test_assert_context_propagated(self):
        """Test context propagation assertion."""
        capture = StructuredLogCapture()
        
        # Add entries with consistent context
        capture.entries = [
            LogEntry("info", "Step 1", {"correlation_id": "req-123", "user_id": "456"}),
            LogEntry("info", "Step 2", {"correlation_id": "req-123", "user_id": "456", "extra": "data"}),
        ]
        
        # Test successful context propagation assertion
        capture.assert_context_propagated(correlation_id="req-123")
        capture.assert_context_propagated(user_id="456")
        capture.assert_context_propagated(correlation_id="req-123", user_id="456")
        
        # Test failed context propagation assertion
        with pytest.raises(AssertionError):
            capture.assert_context_propagated(missing_key="value")
    
    def test_assert_correlation_id_consistent(self):
        """Test correlation ID consistency assertion."""
        capture = StructuredLogCapture()
        
        # Test with consistent correlation IDs
        capture.entries = [
            LogEntry("info", "Step 1", {"correlation_id": "req-123"}),
            LogEntry("info", "Step 2", {"correlation_id": "req-123"}),
        ]
        capture.assert_correlation_id_consistent()
        
        # Test with no correlation IDs (should pass)
        capture.entries = [
            LogEntry("info", "Step 1", {}),
            LogEntry("info", "Step 2", {}),
        ]
        capture.assert_correlation_id_consistent()
        
        # Test with inconsistent correlation IDs
        capture.entries = [
            LogEntry("info", "Step 1", {"correlation_id": "req-123"}),
            LogEntry("info", "Step 2", {"correlation_id": "req-456"}),
        ]
        with pytest.raises(AssertionError):
            capture.assert_correlation_id_consistent()
    
    def test_thread_safety(self):
        """Test thread safety of log capture."""
        capture = StructuredLogCapture()
        
        def log_worker(worker_id):
            for i in range(10):
                capture.add_log_entry('info', f'Message {i}', worker_id=worker_id)
        
        # Start multiple threads
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=log_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all entries were captured
        assert len(capture.entries) == 50  # 5 workers * 10 messages each
        
        # Verify entries from all workers
        worker_ids = {entry.context.get('worker_id') for entry in capture.entries}
        assert worker_ids == {0, 1, 2, 3, 4}


class TestMockStructuredLogger:
    """Test cases for MockStructuredLogger."""
    
    def test_basic_logging(self):
        """Test basic mock logger functionality."""
        mock_logger = MockStructuredLogger("test_logger")
        
        mock_logger.info("Test message", user_id="123")
        mock_logger.warning("Warning message", error_code="404")
        
        assert len(mock_logger.calls) == 2
        
        # Check first call
        first_call = mock_logger.calls[0]
        assert first_call['level'] == 'info'
        assert first_call['message'] == 'Test message'
        assert first_call['context']['user_id'] == '123'
        
        # Check second call
        second_call = mock_logger.calls[1]
        assert second_call['level'] == 'warning'
        assert second_call['message'] == 'Warning message'
        assert second_call['context']['error_code'] == '404'
    
    def test_assert_called_with(self):
        """Test call assertion functionality."""
        mock_logger = MockStructuredLogger()
        
        mock_logger.info("Operation completed", user_id="123", status="success")
        mock_logger.error("Operation failed", user_id="456", error="timeout")
        
        # Test successful assertions
        mock_logger.assert_called_with("Operation completed", level="info")
        mock_logger.assert_called_with("completed", user_id="123")
        mock_logger.assert_called_with("failed", level="error", error="timeout")
        
        # Test count assertions
        mock_logger.assert_called_with("Operation", count=2)  # Both messages contain "Operation"
        mock_logger.assert_called_with("completed", count=1)
        
        # Test failed assertions
        with pytest.raises(AssertionError):
            mock_logger.assert_called_with("Nonexistent message")
        
        with pytest.raises(AssertionError):
            mock_logger.assert_called_with("Operation", count=5)
    
    def test_assert_not_called_with(self):
        """Test negative call assertion functionality."""
        mock_logger = MockStructuredLogger()
        
        mock_logger.info("Test message", user_id="123")
        
        # Test successful negative assertions
        mock_logger.assert_not_called_with("Nonexistent message")
        mock_logger.assert_not_called_with("Test message", level="error")
        mock_logger.assert_not_called_with("Test message", user_id="456")
        
        # Test failed negative assertions
        with pytest.raises(AssertionError):
            mock_logger.assert_not_called_with("Test message")
        
        with pytest.raises(AssertionError):
            mock_logger.assert_not_called_with("Test message", level="info")
    
    def test_get_call_count(self):
        """Test call counting functionality."""
        mock_logger = MockStructuredLogger()
        
        mock_logger.info("Info message 1")
        mock_logger.info("Info message 2")
        mock_logger.warning("Warning message")
        mock_logger.error("Error message")
        
        assert mock_logger.get_call_count() == 4
        assert mock_logger.get_call_count(level="info") == 2
        assert mock_logger.get_call_count(level="warning") == 1
        assert mock_logger.get_call_count(level="error") == 1
        assert mock_logger.get_call_count(level="debug") == 0
    
    def test_thread_safety(self):
        """Test thread safety of mock logger."""
        mock_logger = MockStructuredLogger()
        
        def log_worker(worker_id):
            for i in range(10):
                mock_logger.info(f"Message {i}", worker_id=worker_id)
        
        # Start multiple threads
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=log_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all calls were recorded
        assert len(mock_logger.calls) == 50  # 5 workers * 10 messages each


class TestPerformanceTester:
    """Test cases for PerformanceTester."""
    
    def test_performance_measurement(self):
        """Test basic performance measurement."""
        tester = PerformanceTester(max_duration_ms=100.0)
        
        # Simulate some operations
        for _ in range(5):
            with tester.measure_operation():
                time.sleep(0.001)  # 1ms sleep
        
        metrics = tester.metrics
        assert metrics.operation_count == 5
        assert metrics.avg_duration_ms >= 1.0  # Should be at least 1ms
        assert metrics.min_duration_ms > 0
        assert metrics.max_duration_ms >= metrics.min_duration_ms
        assert metrics.total_duration_ms >= 5.0  # At least 5ms total
    
    def test_performance_assertion_success(self):
        """Test successful performance assertion."""
        tester = PerformanceTester(max_duration_ms=10.0)
        
        # Fast operations should pass
        for _ in range(3):
            with tester.measure_operation():
                pass  # No-op, should be very fast
        
        # Should not raise an assertion error
        tester.assert_performance_acceptable()
    
    def test_performance_assertion_failure(self):
        """Test failed performance assertion."""
        tester = PerformanceTester(max_duration_ms=0.5)  # Strict but reasonable limit
        
        # Slow operation should fail
        with tester.measure_operation():
            time.sleep(0.002)  # 2ms sleep, exceeds 0.5ms limit
        
        # Should raise an assertion error
        with pytest.raises(AssertionError):
            tester.assert_performance_acceptable()
    
    def test_overhead_calculation(self):
        """Test overhead calculation against baseline."""
        tester = PerformanceTester(max_overhead_percentage=1000.0)  # Extremely lenient for test environments
        
        # Simulate operations with longer baseline to reduce relative overhead
        baseline_ms = 1.0  # 1ms baseline for more stable measurements
        for _ in range(5):
            with tester.measure_operation():
                time.sleep(0.001)  # 1ms sleep
        
        # Should pass with 1000% overhead limit (extremely lenient for CI environments)
        tester.assert_performance_acceptable(baseline_ms=baseline_ms)
        
        # Check that overhead was calculated
        assert tester.metrics.overhead_percentage >= 0
    
    def test_get_summary(self):
        """Test performance summary generation."""
        tester = PerformanceTester()
        
        # Add some measurements
        for i in range(3):
            with tester.measure_operation():
                time.sleep(0.001 * (i + 1))  # Variable sleep times
        
        summary = tester.get_summary()
        
        assert 'operation_count' in summary
        assert 'avg_duration_ms' in summary
        assert 'min_duration_ms' in summary
        assert 'max_duration_ms' in summary
        assert 'total_duration_ms' in summary
        assert 'overhead_percentage' in summary
        
        assert summary['operation_count'] == 3
        assert summary['avg_duration_ms'] > 0
        assert summary['min_duration_ms'] <= summary['max_duration_ms']


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_create_test_context(self):
        """Test test context creation."""
        # Test with defaults
        context = create_test_context()
        assert context.correlation_id == 'test-correlation-123'
        assert context.user_id == 'test-user-456'
        assert context.operation == 'test_operation'
        
        # Test with custom values (only valid LoggingContext fields)
        context = create_test_context(
            correlation_id='custom-123',
            user_id='custom-user',
            operation='custom_operation'
        )
        assert context.correlation_id == 'custom-123'
        assert context.user_id == 'custom-user'
        assert context.operation == 'custom_operation'
    
    def test_assert_log_performance(self):
        """Test log performance assertion utility."""
        def fast_function():
            pass  # No-op, should be very fast
        
        def slow_function():
            time.sleep(0.002)  # 2ms sleep
        
        # Fast function should pass
        summary = assert_log_performance(fast_function, max_duration_ms=1.0, iterations=5)
        assert summary['operation_count'] == 5
        assert summary['avg_duration_ms'] < 1.0
        
        # Slow function should fail
        with pytest.raises(AssertionError):
            assert_log_performance(slow_function, max_duration_ms=0.5, iterations=3)


class TestDecorators:
    """Test cases for testing decorators."""
    
    def test_performance_test_decorator(self):
        """Test performance test decorator."""
        call_count = 0
        
        @performance_test(max_overhead_ms=1.0, iterations=5)
        def fast_test_function():
            nonlocal call_count
            call_count += 1
        
        # Should execute without raising an assertion error
        fast_test_function()
        
        # Should have been called the specified number of iterations
        assert call_count == 5
    
    def test_with_isolated_context_decorator(self):
        """Test isolated context decorator."""
        # Set some initial context
        with LoggingContext(user_id="initial-user"):
            assert get_current_context().user_id == "initial-user"
            
            @with_isolated_context
            def test_function():
                # Context should be cleared
                context = get_current_context()
                assert context.user_id is None
                
                # Set new context
                with LoggingContext(user_id="test-user"):
                    pass
            
            test_function()
            
            # Original context should be restored
            assert get_current_context().user_id == "initial-user"


class TestContextManagers:
    """Test cases for context managers."""
    
    def test_temporary_log_capture(self):
        """Test temporary log capture context manager."""
        with temporary_log_capture() as capture:
            # Add log entry manually
            capture.add_log_entry('info', 'Test message')
            
            assert len(capture.entries) == 1
            assert capture.entries[0].message == "Test message"
        
        # Capture should be stopped after context exit
        # (No easy way to test this without more complex setup)
    
    def test_mock_structured_logger_context(self):
        """Test mock structured logger context manager."""
        with mock_structured_logger("test_logger") as mock_logger:
            assert mock_logger.name == "test_logger"
            assert len(mock_logger.calls) == 0
            
            # Mock should be available for testing
            mock_logger.info("Test message")
            assert len(mock_logger.calls) == 1


class TestLoggingTestPatterns:
    """Test cases for LoggingTestPatterns."""
    
    def test_basic_logging_pattern(self, log_capture):
        """Test basic logging test pattern."""
        mock_logger = MockStructuredLogger()
        
        LoggingTestPatterns.test_basic_logging(mock_logger, log_capture)
        
        # Verify the pattern worked
        mock_logger.assert_called_with("Test message", level="info", key="value")
    
    def test_context_propagation_pattern(self, log_capture, isolated_context):
        """Test context propagation test pattern."""
        mock_logger = MockStructuredLogger()
        
        LoggingTestPatterns.test_context_propagation(mock_logger, log_capture)
        
        # Verify the pattern worked
        mock_logger.assert_called_with("Operation started", user_id="test-123", operation="test_op")
    
    def test_error_logging_pattern(self, log_capture):
        """Test error logging test pattern."""
        mock_logger = MockStructuredLogger()
        
        LoggingTestPatterns.test_error_logging(mock_logger, log_capture)
        
        # Verify the pattern worked
        mock_logger.assert_called_with("Operation failed", level="error")
    
    def test_performance_logging_pattern(self, performance_tester):
        """Test performance logging test pattern."""
        mock_logger = MockStructuredLogger()
        
        LoggingTestPatterns.test_performance_logging(mock_logger, performance_tester)
        
        # Verify the pattern worked
        mock_logger.assert_called_with("Performance test message")
        assert performance_tester.metrics.operation_count == 1


# Integration Tests
class TestTestingIntegration:
    """Integration tests for testing infrastructure."""
    
    def test_full_testing_workflow(self, log_capture, isolated_context, performance_tester):
        """Test complete testing workflow with all components."""
        # Create a mock logger
        mock_logger = MockStructuredLogger("integration_test")
        
        # Set up context
        with LoggingContext(correlation_id="int-test-123", user_id="test-user"):
            # Perform logging operations
            with performance_tester.measure_operation():
                mock_logger.info("Integration test started", operation="full_test")
                mock_logger.warning("Test warning", component="testing")
                mock_logger.info("Integration test completed", status="success")
        
        # Verify all aspects
        assert mock_logger.get_call_count() == 3
        assert mock_logger.get_call_count(level="info") == 2
        assert mock_logger.get_call_count(level="warning") == 1
        
        mock_logger.assert_called_with("Integration test started", level="info", operation="full_test")
        mock_logger.assert_called_with("Test warning", level="warning", component="testing")
        mock_logger.assert_called_with("Integration test completed", level="info", status="success")
        
        # Verify performance
        performance_tester.assert_performance_acceptable()
        summary = performance_tester.get_summary()
        assert summary['operation_count'] == 1
        assert summary['avg_duration_ms'] >= 0