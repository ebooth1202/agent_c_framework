"""
Test configuration for structured logging tests.
"""

import pytest
from agent_c.util.structured_logging.factory import StructuredLoggerFactory
from agent_c.util.structured_logging.testing import (
    StructuredLogCapture,
    MockStructuredLogger,
    PerformanceTester
)
from agent_c.util.structured_logging.context import LoggingContext, clear_context


@pytest.fixture(autouse=True)
def reset_factory():
    """Reset the factory singleton before each test."""
    StructuredLoggerFactory.reset()
    yield
    StructuredLoggerFactory.reset()


@pytest.fixture
def log_capture():
    """Provide a StructuredLogCapture instance for testing."""
    capture = StructuredLogCapture()
    capture.start_capture()
    yield capture
    capture.stop_capture()


@pytest.fixture
def mock_logger():
    """Provide a MockStructuredLogger instance for testing."""
    return MockStructuredLogger("test_logger")


@pytest.fixture
def isolated_context():
    """Ensure clean logging context for each test."""
    # Clear any existing context
    clear_context()
    yield
    # Clear context after test
    clear_context()


@pytest.fixture
def performance_tester():
    """Provide a PerformanceTester instance for testing."""
    return PerformanceTester(max_overhead_percentage=1000.0, max_duration_ms=50.0)


@pytest.fixture
def factory_reset():
    """Reset StructuredLoggerFactory between tests."""
    StructuredLoggerFactory.reset()
    yield
    StructuredLoggerFactory.reset()