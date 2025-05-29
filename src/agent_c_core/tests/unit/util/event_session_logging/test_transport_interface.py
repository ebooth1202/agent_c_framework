#!/usr/bin/env python3
"""
Transport Interface Test Suite - Pytest Version

This script tests the TransportInterface abstraction and various concrete implementations
to validate the transport layer functionality for future decoupling.
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
import pytest

# Add the src directory to Python path for imports
agent_c_core_dir = Path(__file__).parents[4]
sys.path.insert(0, str(agent_c_core_dir / 'src'))

from agent_c.util.transports import (
    TransportInterface, TransportState, TransportMetrics,
    CallbackTransport, LoggingTransport, NullTransport, FileTransport,
    HTTPTransport, QueueTransport, RetryTransport
)
from agent_c.util.transport_exceptions import TransportError, TransportConnectionError
from agent_c.models.events.chat import MessageEvent, TextDeltaEvent


class FailingTransport(TransportInterface):
    """Test transport that always fails"""

    def __init__(self, fail_on_connect: bool = False):
        super().__init__("FailingTransport")
        self.fail_on_connect = fail_on_connect
        self.send_attempts = 0
        self.connect_attempts = 0

    async def send(self, event, metadata=None) -> bool:
        self.send_attempts += 1
        raise TransportError("Simulated transport failure")

    async def connect(self) -> bool:
        self.connect_attempts += 1
        if self.fail_on_connect:
            raise TransportConnectionError("Simulated connection failure")
        self.state = TransportState.CONNECTED
        return True

    async def disconnect(self) -> None:
        self.state = TransportState.DISCONNECTED

    async def close(self) -> None:
        await self.disconnect()
        self.state = TransportState.CLOSED


class SlowTransport(TransportInterface):
    """Test transport with configurable delays"""

    def __init__(self, send_delay: float = 0.1, connect_delay: float = 0.05):
        super().__init__("SlowTransport")
        self.send_delay = send_delay
        self.connect_delay = connect_delay
        self.sent_events = []

    async def send(self, event, metadata=None) -> bool:
        await asyncio.sleep(self.send_delay)
        self.sent_events.append(event)
        return True

    async def connect(self) -> bool:
        await asyncio.sleep(self.connect_delay)
        self.state = TransportState.CONNECTED
        return True

    async def disconnect(self) -> None:
        self.state = TransportState.DISCONNECTED

    async def close(self) -> None:
        await self.disconnect()
        self.state = TransportState.CLOSED


# Pytest fixtures
@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_message_event():
    """Provide a sample MessageEvent for testing"""
    return MessageEvent(
        session_id="test_session",
        role="assistant",
        content="Test message"
    )


@pytest.fixture
def sample_text_delta_event():
    """Provide a sample TextDeltaEvent for testing"""
    return TextDeltaEvent(
        session_id="test_session",
        role="assistant",
        content="Test delta"
    )


@pytest.fixture
async def connected_null_transport():
    """Provide a connected NullTransport for testing"""
    transport = NullTransport()
    await transport.connect()
    yield transport
    await transport.close()


# Test functions with pytest decorators
@pytest.mark.asyncio
async def test_transport_interface_basics():
    """Test basic transport interface functionality"""
    # Test NullTransport
    transport = NullTransport()

    # Test initial state
    assert transport.state == TransportState.CONNECTED, "NullTransport should start connected"
    assert transport.is_connected == True, "Should be connected"

    # Test send
    event = {"type": "test", "data": "test event"}
    result = await transport.send(event)
    assert result == True, "Send should succeed"

    # Test metrics
    assert transport.metrics.total_sent == 1, "Should track sent events"
    assert transport.metrics.total_failed == 0, "Should have no failures"
    assert transport.metrics.success_rate == 100.0, "Should have 100% success rate"

    # Test health check
    health = await transport.health_check()
    assert health == True, "Should be healthy"

    # Test close
    await transport.close()
    assert transport.state == TransportState.CLOSED, "Should be closed"


@pytest.mark.asyncio
async def test_callback_transport(sample_message_event):
    """Test CallbackTransport functionality"""
    # Test with sync callback
    received_events = []

    def sync_callback(event):
        received_events.append(event)

    transport = CallbackTransport(sync_callback)

    # Test send
    result = await transport.send(sample_message_event)
    assert result == True, "Send should succeed"
    assert len(received_events) == 1, "Callback should receive event"

    # Test with async callback
    async_received = []

    async def async_callback(event):
        async_received.append(event)

    async_transport = CallbackTransport(async_callback)
    result = await async_transport.send(sample_message_event)
    assert result == True, "Async send should succeed"
    assert len(async_received) == 1, "Async callback should receive event"

    await transport.close()
    await async_transport.close()


@pytest.mark.asyncio
async def test_logging_transport(sample_text_delta_event):
    """Test LoggingTransport functionality"""
    import logging
    from io import StringIO

    # Capture log output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("test_transport")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    transport = LoggingTransport("test_transport", logging.INFO)

    # Test send
    result = await transport.send(sample_text_delta_event)
    assert result == True, "Send should succeed"

    # Check log output
    log_output = log_capture.getvalue()
    assert "Transport event:" in log_output, "Should log transport event"
    assert "test_session" in log_output, "Should include session_id"

    await transport.close()


@pytest.mark.asyncio
async def test_file_transport(temp_dir, sample_message_event):
    """Test FileTransport functionality"""
    file_path = Path(temp_dir) / "transport_test.jsonl"

    transport = FileTransport(str(file_path))

    # Test connection
    await transport.connect()
    assert transport.is_connected == True, "Should be connected"

    # Test send
    event = {"type": "test", "data": "file transport test"}
    result = await transport.send(event, {"routing": "test"})
    assert result == True, "Send should succeed"

    # Test another event
    result2 = await transport.send(sample_message_event)
    assert result2 == True, "Second send should succeed"

    await transport.close()

    # Verify file contents
    assert file_path.exists(), "File should be created"

    with open(file_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2, "Should have 2 log entries"

        # Parse first entry
        entry1 = json.loads(lines[0])
        assert entry1["transport"] == "FileTransport", "Should include transport name"
        assert entry1["event"]["type"] == "test", "Should include event data"
        assert entry1["metadata"]["routing"] == "test", "Should include metadata"

        # Parse second entry
        entry2 = json.loads(lines[1])
        assert entry2["event"]["session_id"] == "test_session", "Should include session_id"


@pytest.mark.asyncio
async def test_http_transport():
    """Test HTTPTransport functionality (placeholder implementation)"""
    transport = HTTPTransport("https://example.com/webhook")

    # Test connection
    await transport.connect()
    assert transport.is_connected == True, "Should be connected"

    # Test send (placeholder implementation)
    event = {"type": "http_test", "data": "HTTP transport test"}
    result = await transport.send(event, {"endpoint": "webhook"})
    assert result == True, "Send should succeed (placeholder)"

    # Test metrics
    assert transport.metrics.total_sent == 1, "Should track sent events"
    assert transport.metrics.success_rate == 100.0, "Should have success"

    await transport.close()


@pytest.mark.asyncio
async def test_queue_transport():
    """Test QueueTransport functionality (placeholder implementation)"""
    transport = QueueTransport("test_queue", "amqp://localhost")

    # Test connection
    await transport.connect()
    assert transport.is_connected == True, "Should be connected"

    # Test send (placeholder implementation)
    event = {"type": "queue_test", "data": "Queue transport test"}
    result = await transport.send(event, {"queue": "test_queue"})
    assert result == True, "Send should succeed (placeholder)"

    await transport.close()


@pytest.mark.asyncio
async def test_retry_transport():
    """Test RetryTransport with retry logic"""
    # Test with failing transport
    failing_transport = FailingTransport()
    retry_transport = RetryTransport(failing_transport, max_retries=2, base_delay=0.01)

    await retry_transport.connect()

    # Test send with retries
    event = {"type": "retry_test", "data": "Retry test"}
    result = await retry_transport.send(event)
    assert result == False, "Should fail after retries"
    assert failing_transport.send_attempts == 3, "Should attempt 3 times (initial + 2 retries)"
    assert retry_transport.metrics.total_retries == 2, "Should track retries"

    await retry_transport.close()

    # Test with fallback transport
    fallback_transport = NullTransport()
    await fallback_transport.connect()

    retry_with_fallback = RetryTransport(
        FailingTransport(),
        max_retries=1,
        base_delay=0.01,
        fallback_transport=fallback_transport
    )

    await retry_with_fallback.connect()

    result = await retry_with_fallback.send(event)
    assert result == True, "Should succeed with fallback"
    assert fallback_transport.metrics.total_sent == 1, "Fallback should receive event"

    await retry_with_fallback.close()


@pytest.mark.asyncio
async def test_transport_metrics(connected_null_transport):
    """Test transport metrics functionality"""
    transport = connected_null_transport

    # Send multiple events
    for i in range(5):
        event = {"type": "metrics_test", "index": i}
        await transport.send(event)

    # Check metrics
    assert transport.metrics.total_sent == 5, "Should track all sent events"
    assert transport.metrics.total_failed == 0, "Should have no failures"
    assert transport.metrics.success_rate == 100.0, "Should have 100% success"
    assert transport.metrics.is_healthy == True, "Should be healthy"
    assert transport.metrics.last_success_time is not None, "Should track last success"


@pytest.mark.asyncio
async def test_transport_states(temp_dir):
    """Test transport state management"""
    transport = FileTransport(f"{temp_dir}/test_state.jsonl")

    # Test initial state
    assert transport.state == TransportState.DISCONNECTED, "Should start disconnected"
    assert not transport.is_connected, "Should not be connected"

    # Test connection
    await transport.connect()
    assert transport.state == TransportState.CONNECTED, "Should be connected"
    assert transport.is_connected, "Should report connected"

    # Test disconnection
    await transport.disconnect()
    assert transport.state == TransportState.DISCONNECTED, "Should be disconnected"
    assert not transport.is_connected, "Should not be connected"

    # Test close
    await transport.close()
    assert transport.state == TransportState.CLOSED, "Should be closed"


@pytest.mark.asyncio
async def test_async_context_manager(temp_dir):
    """Test transport async context manager"""
    file_path = Path(temp_dir) / "context_test.jsonl"

    # Test context manager
    async with FileTransport(str(file_path)) as transport:
        assert transport.is_connected, "Should be connected in context"

        event = {"type": "context_test", "data": "Context manager test"}
        result = await transport.send(event)
        assert result == True, "Send should succeed"

    # Transport should be closed after context
    assert transport.state == TransportState.CLOSED, "Should be closed after context"

    # File should still exist with content
    assert file_path.exists(), "File should exist"
    with open(file_path, 'r') as f:
        content = f.read()
        assert "context_test" in content, "Should contain event data"


@pytest.mark.asyncio
async def test_performance_characteristics():
    """Test transport performance characteristics"""
    # Test NullTransport performance
    null_transport = NullTransport()
    await null_transport.connect()

    start_time = time.time()
    for i in range(100):
        event = {"type": "perf_test", "index": i}
        await null_transport.send(event)
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = null_transport.metrics.average_send_time

    assert total_time < 2.0, "100 events should complete reasonably quickly"
    assert avg_time > 0, "Should track average send time"
    assert null_transport.metrics.total_sent == 100, "Should track all events"

    await null_transport.close()

    # Test SlowTransport with timing
    slow_transport = SlowTransport(send_delay=0.01)
    await slow_transport.connect()

    start_time = time.time()
    await slow_transport.send({"type": "slow_test"})
    end_time = time.time()

    assert (end_time - start_time) >= 0.01, "Should respect delay"
    assert len(slow_transport.sent_events) == 1, "Should track sent events"

    await slow_transport.close()