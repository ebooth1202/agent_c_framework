"""
Test configuration for structured logging tests.
"""

import pytest
from agent_c.util.structured_logging.factory import StructuredLoggerFactory


@pytest.fixture(autouse=True)
def reset_factory():
    """Reset the factory singleton before each test."""
    StructuredLoggerFactory.reset()
    yield
    StructuredLoggerFactory.reset()