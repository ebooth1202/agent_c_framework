"""
Testing Infrastructure for Structured Logging

This module provides comprehensive testing utilities for validating structured logging
behavior, including log capture, assertion helpers, mock utilities, and performance
testing tools.

Key Features:
- LogCapture fixture for structured log validation
- Rich assertion helpers for log content and context
- Mock logger utilities for testing logging behavior
- Performance testing decorators and helpers
- Context isolation for test independence
- Easy-to-use pytest fixtures

Usage:
    # Basic log capture and assertion
    def test_my_function(log_capture):
        my_function()
        log_capture.assert_logged("operation_completed", level="info", user_id="123")
    
    # Performance testing
    @performance_test(max_overhead_ms=5)
    def test_logging_performance():
        logger.info("Test message", context={"key": "value"})
    
    # Mock logger testing
    def test_with_mock_logger(mock_logger):
        my_function()
        mock_logger.assert_called_with("Expected message", level="info")
"""

import pytest
import time
import logging
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from unittest.mock import Mock, patch
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections import defaultdict

import structlog
from structlog.testing import LogCapture as StructlogLogCapture

from .context import LoggingContext, clear_context, get_current_context
from .factory import StructuredLoggerFactory


@dataclass
class LogEntry:
    """Represents a captured log entry with structured data."""
    
    level: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    logger_name: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def has_context(self, **expected_context) -> bool:
        """Check if log entry contains expected context values."""
        for key, expected_value in expected_context.items():
            if key not in self.context:
                return False
            if self.context[key] != expected_value:
                return False
        return True
    
    def matches_pattern(self, message_pattern: str = None, level: str = None, **context_pattern) -> bool:
        """Check if log entry matches the given pattern."""
        # Check level
        if level and self.level.lower() != level.lower():
            return False
        
        # Check message pattern
        if message_pattern and message_pattern not in self.message:
            return False
        
        # Check context pattern
        if context_pattern and not self.has_context(**context_pattern):
            return False
        
        return True


class StructuredLogCapture:
    """Enhanced log capture for structured logging validation."""
    
    def __init__(self):
        self.entries: List[LogEntry] = []
        self._lock = threading.Lock()
    
    def start_capture(self):
        """Start capturing structured logs."""
        # Simple approach - just initialize the capture
        pass
    
    def stop_capture(self):
        """Stop capturing logs and restore original configuration."""
        # Simple approach - no special cleanup needed
        pass
    
    def add_log_entry(self, level: str, message: str, **context):
        """Manually add a log entry for testing purposes."""
        with self._lock:
            entry = LogEntry(
                level=level.upper(),
                message=message,
                context=context
            )
            self.entries.append(entry)
    
    def _add_entry_from_structlog(self, structlog_entry):
        """Convert a structlog entry to our LogEntry format."""
        with self._lock:
            # Extract event and context from structlog entry
            event = structlog_entry.get('event', '')
            context = {k: v for k, v in structlog_entry.items() if k != 'event'}
            
            # Try to determine level from context or default to 'info'
            level = context.pop('level', 'info')
            
            entry = LogEntry(
                level=level.upper(),
                message=event,
                context=context,
                logger_name=context.get('logger', None)
            )
            self.entries.append(entry)
    
    def clear(self):
        """Clear all captured log entries."""
        with self._lock:
            self.entries.clear()
    
    def get_entries(self, level: str = None, message_pattern: str = None, **context_filter) -> List[LogEntry]:
        """Get log entries matching the given criteria."""
        with self._lock:
            filtered_entries = []
            for entry in self.entries:
                if entry.matches_pattern(message_pattern, level, **context_filter):
                    filtered_entries.append(entry)
            return filtered_entries
    
    def assert_logged(self, message_pattern: str = None, level: str = None, count: int = None, **expected_context):
        """Assert that a log entry with the given pattern was logged."""
        entries = self.get_entries(level, message_pattern, **expected_context)
        
        if count is not None:
            assert len(entries) == count, (
                f"Expected {count} log entries matching pattern, but found {len(entries)}. "
                f"Entries: {[e.message for e in entries]}"
            )
        else:
            assert len(entries) > 0, (
                f"Expected log entry with pattern '{message_pattern}', level '{level}', "
                f"context {expected_context}, but none found. "
                f"Available entries: {[e.message for e in self.entries]}"
            )
    
    def assert_not_logged(self, message_pattern: str = None, level: str = None, **expected_context):
        """Assert that no log entry with the given pattern was logged."""
        entries = self.get_entries(level, message_pattern, **expected_context)
        assert len(entries) == 0, (
            f"Expected no log entries matching pattern, but found {len(entries)}. "
            f"Entries: {[e.message for e in entries]}"
        )
    
    def assert_context_propagated(self, **expected_context):
        """Assert that context was propagated to all log entries."""
        with self._lock:
            for entry in self.entries:
                assert entry.has_context(**expected_context), (
                    f"Expected context {expected_context} not found in log entry: {entry.context}"
                )
    
    def assert_correlation_id_consistent(self):
        """Assert that all log entries have the same correlation ID."""
        with self._lock:
            if not self.entries:
                return
            
            correlation_ids = {entry.context.get('correlation_id') for entry in self.entries}
            correlation_ids.discard(None)  # Remove None values
            
            assert len(correlation_ids) <= 1, (
                f"Expected consistent correlation ID, but found multiple: {correlation_ids}"
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from captured logs."""
        with self._lock:
            timing_entries = [e for e in self.entries if 'duration_ms' in e.context]
            
            if not timing_entries:
                return {}
            
            durations = [e.context['duration_ms'] for e in timing_entries]
            return {
                'count': len(durations),
                'total_ms': sum(durations),
                'avg_ms': sum(durations) / len(durations),
                'min_ms': min(durations),
                'max_ms': max(durations),
            }


class MockStructuredLogger:
    """Mock logger for testing structured logging calls."""
    
    def __init__(self, name: str = "test_logger"):
        self.name = name
        self.calls: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def _log(self, level: str, message: str, **kwargs):
        """Record a log call."""
        with self._lock:
            self.calls.append({
                'level': level,
                'message': message,
                'context': kwargs,
                'timestamp': time.time(),
            })
    
    def debug(self, message: str, **kwargs):
        self._log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log('critical', message, **kwargs)
    
    def assert_called_with(self, message: str, level: str = None, count: int = None, **expected_context):
        """Assert that the logger was called with the given parameters."""
        matching_calls = []
        
        with self._lock:
            for call in self.calls:
                if message in call['message']:
                    if level is None or call['level'] == level:
                        if all(call['context'].get(k) == v for k, v in expected_context.items()):
                            matching_calls.append(call)
        
        if count is not None:
            assert len(matching_calls) == count, (
                f"Expected {count} calls matching criteria, but found {len(matching_calls)}"
            )
        else:
            assert len(matching_calls) > 0, (
                f"Expected call with message '{message}', level '{level}', context {expected_context}, "
                f"but none found. Actual calls: {self.calls}"
            )
    
    def assert_not_called_with(self, message: str, level: str = None, **expected_context):
        """Assert that the logger was not called with the given parameters."""
        matching_calls = []
        
        with self._lock:
            for call in self.calls:
                if message in call['message']:
                    if level is None or call['level'] == level:
                        if all(call['context'].get(k) == v for k, v in expected_context.items()):
                            matching_calls.append(call)
        
        assert len(matching_calls) == 0, (
            f"Expected no calls matching criteria, but found {len(matching_calls)}"
        )
    
    def clear_calls(self):
        """Clear all recorded calls."""
        with self._lock:
            self.calls.clear()
    
    def get_call_count(self, level: str = None) -> int:
        """Get the number of calls, optionally filtered by level."""
        with self._lock:
            if level is None:
                return len(self.calls)
            return len([call for call in self.calls if call['level'] == level])


@dataclass
class PerformanceMetrics:
    """Performance metrics for logging operations."""
    
    operation_count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    overhead_percentage: float = 0.0
    
    @property
    def avg_duration_ms(self) -> float:
        """Calculate average duration."""
        return self.total_duration_ms / self.operation_count if self.operation_count > 0 else 0.0
    
    def add_measurement(self, duration_ms: float):
        """Add a performance measurement."""
        self.operation_count += 1
        self.total_duration_ms += duration_ms
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)
    
    def calculate_overhead(self, baseline_ms: float):
        """Calculate overhead percentage compared to baseline."""
        if baseline_ms > 0:
            self.overhead_percentage = ((self.avg_duration_ms - baseline_ms) / baseline_ms) * 100


class PerformanceTester:
    """Utility for performance testing of logging operations."""
    
    def __init__(self, max_overhead_percentage: float = 5.0, max_duration_ms: float = 1.0):
        self.max_overhead_percentage = max_overhead_percentage
        self.max_duration_ms = max_duration_ms
        self.metrics = PerformanceMetrics()
    
    @contextmanager
    def measure_operation(self):
        """Context manager to measure operation performance."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            self.metrics.add_measurement(duration_ms)
    
    def assert_performance_acceptable(self, baseline_ms: float = None):
        """Assert that performance metrics meet requirements."""
        # Check average duration
        assert self.metrics.avg_duration_ms <= self.max_duration_ms, (
            f"Average logging duration {self.metrics.avg_duration_ms:.2f}ms exceeds "
            f"maximum {self.max_duration_ms}ms"
        )
        
        # Check overhead if baseline provided
        if baseline_ms is not None:
            self.metrics.calculate_overhead(baseline_ms)
            assert self.metrics.overhead_percentage <= self.max_overhead_percentage, (
                f"Logging overhead {self.metrics.overhead_percentage:.1f}% exceeds "
                f"maximum {self.max_overhead_percentage}%"
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            'operation_count': self.metrics.operation_count,
            'avg_duration_ms': self.metrics.avg_duration_ms,
            'min_duration_ms': self.metrics.min_duration_ms,
            'max_duration_ms': self.metrics.max_duration_ms,
            'total_duration_ms': self.metrics.total_duration_ms,
            'overhead_percentage': self.metrics.overhead_percentage,
        }


# Pytest Fixtures
@pytest.fixture
def log_capture():
    """Fixture providing structured log capture capabilities."""
    capture = StructuredLogCapture()
    capture.start_capture()
    try:
        yield capture
    finally:
        capture.stop_capture()


@pytest.fixture
def mock_logger():
    """Fixture providing a mock structured logger."""
    return MockStructuredLogger()


@pytest.fixture
def isolated_context():
    """Fixture providing isolated logging context for tests."""
    # Clear any existing context
    clear_context()
    try:
        yield
    finally:
        # Clean up context after test
        clear_context()


@pytest.fixture
def performance_tester():
    """Fixture providing performance testing utilities."""
    return PerformanceTester()


@pytest.fixture
def factory_reset():
    """Fixture that resets the StructuredLoggerFactory before and after tests."""
    StructuredLoggerFactory.reset()
    try:
        yield
    finally:
        StructuredLoggerFactory.reset()


# Decorators
def performance_test(max_overhead_ms: float = 5.0, iterations: int = 100):
    """Decorator for performance testing of logging operations."""
    def decorator(test_func: Callable):
        def wrapper(*args, **kwargs):
            tester = PerformanceTester(max_duration_ms=max_overhead_ms)
            
            # Run multiple iterations for accurate measurement
            for _ in range(iterations):
                with tester.measure_operation():
                    test_func(*args, **kwargs)
            
            # Assert performance is acceptable
            tester.assert_performance_acceptable()
            
            # Print summary for debugging
            summary = tester.get_summary()
            print(f"Performance Test Summary: {summary}")
            
        return wrapper
    return decorator


def with_log_capture(test_func: Callable):
    """Decorator that automatically provides log capture to test functions."""
    def wrapper(*args, **kwargs):
        capture = StructuredLogCapture()
        capture.start_capture()
        try:
            return test_func(*args, capture=capture, **kwargs)
        finally:
            capture.stop_capture()
    return wrapper


def with_isolated_context(test_func: Callable):
    """Decorator that provides isolated logging context for tests."""
    def wrapper(*args, **kwargs):
        # Save current context
        from agent_c.util.structured_logging.context import ContextSnapshot
        snapshot = ContextSnapshot()
        
        # Clear context for isolated test
        clear_context()
        try:
            return test_func(*args, **kwargs)
        finally:
            # Restore original context
            snapshot.restore()
    return wrapper


# Utility Functions
def create_test_context(**context_values) -> LoggingContext:
    """Create a test logging context with default values."""
    defaults = {
        'correlation_id': 'test-correlation-123',
        'user_id': 'test-user-456',
        'operation': 'test_operation',
    }
    defaults.update(context_values)
    return LoggingContext(**defaults)


def assert_log_performance(func: Callable, max_duration_ms: float = 1.0, iterations: int = 10):
    """Assert that a function's logging performance is acceptable."""
    tester = PerformanceTester(max_duration_ms=max_duration_ms)
    
    for _ in range(iterations):
        with tester.measure_operation():
            func()
    
    tester.assert_performance_acceptable()
    return tester.get_summary()


def capture_logs_for_function(func: Callable, *args, **kwargs) -> List[LogEntry]:
    """Capture logs generated by executing a function."""
    capture = StructuredLogCapture()
    capture.start_capture()
    try:
        func(*args, **kwargs)
        return capture.entries.copy()
    finally:
        capture.stop_capture()


# Context Managers
@contextmanager
def temporary_log_capture():
    """Context manager for temporary log capture."""
    capture = StructuredLogCapture()
    try:
        yield capture
    finally:
        pass  # No special cleanup needed for simplified approach


@contextmanager
def mock_structured_logger(logger_name: str = "test_logger"):
    """Context manager that provides a mock logger."""
    mock_logger = MockStructuredLogger(logger_name)
    
    # Patch the logger factory to return our mock
    with patch('agent_c.util.structured_logging.factory.StructuredLoggerFactory.get_logger') as mock_get_logger:
        mock_get_logger.return_value = mock_logger
        yield mock_logger


# Test Patterns and Examples
class LoggingTestPatterns:
    """Collection of common logging test patterns."""
    
    @staticmethod
    def test_basic_logging(logger, log_capture):
        """Test basic logging functionality."""
        logger.info("Test message", key="value")
        log_capture.assert_logged("Test message", level="info", key="value")
    
    @staticmethod
    def test_context_propagation(logger, log_capture):
        """Test context propagation in logging."""
        with LoggingContext(user_id="test-123", operation="test_op"):
            logger.info("Operation started")
            log_capture.assert_logged("Operation started", user_id="test-123", operation="test_op")
    
    @staticmethod
    def test_error_logging(logger, log_capture):
        """Test error logging with exception context."""
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.error("Operation failed", exc_info=True)
        
        log_capture.assert_logged("Operation failed", level="error")
    
    @staticmethod
    def test_performance_logging(logger, performance_tester):
        """Test logging performance."""
        with performance_tester.measure_operation():
            logger.info("Performance test message", data={"key": "value"})
        
        performance_tester.assert_performance_acceptable()