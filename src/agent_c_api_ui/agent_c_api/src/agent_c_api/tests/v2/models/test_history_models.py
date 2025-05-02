# src/agent_c_api/tests/v2/models/test_history_models.py
import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from agent_c_api.api.v2.models.history_models import (
    HistorySummary, EventFilter, Event, ReplayStatus, ReplayControl
)

def test_history_summary():
    session_id = uuid4()
    now = datetime.now()
    
    # Test valid history summary
    summary = HistorySummary(
        session_id=session_id,
        name="Test Session",
        created_at=now,
        updated_at=now + timedelta(hours=1),
        message_count=10,
        duration=3600  # 1 hour in seconds
    )
    
    assert summary.session_id == session_id
    assert summary.name == "Test Session"
    assert summary.created_at == now
    assert summary.updated_at == now + timedelta(hours=1)
    assert summary.message_count == 10
    assert summary.duration == 3600
    
    # Test with missing required field
    with pytest.raises(ValueError):
        HistorySummary(
            session_id=session_id,
            # name is missing
            created_at=now,
            updated_at=now,
            message_count=10,
            duration=3600
        )

def test_event_filter():
    now = datetime.now()
    
    # Test with defaults
    filter = EventFilter()
    assert filter.event_types is None
    assert filter.start_time is None
    assert filter.end_time is None
    assert filter.limit == 100
    
    # Test with custom values
    filter = EventFilter(
        event_types=["message", "tool_call"],
        start_time=now - timedelta(hours=1),
        end_time=now,
        limit=50
    )
    assert filter.event_types == ["message", "tool_call"]
    assert filter.start_time == now - timedelta(hours=1)
    assert filter.end_time == now
    assert filter.limit == 50

def test_event():
    session_id = uuid4()
    now = datetime.now()
    
    # Test valid event
    event = Event(
        id="evt-123",
        session_id=session_id,
        timestamp=now,
        event_type="message",
        data={"text": "Hello, world!"}
    )
    
    assert event.id == "evt-123"
    assert event.session_id == session_id
    assert event.timestamp == now
    assert event.event_type == "message"
    assert event.data == {"text": "Hello, world!"}

def test_replay_status():
    session_id = uuid4()
    now = datetime.now()
    
    # Test valid replay status
    status = ReplayStatus(
        session_id=session_id,
        is_playing=True,
        current_position=now + timedelta(minutes=30),
        start_time=now,
        end_time=now + timedelta(hours=1)
    )
    
    assert status.session_id == session_id
    assert status.is_playing is True
    assert status.current_position == now + timedelta(minutes=30)
    assert status.start_time == now
    assert status.end_time == now + timedelta(hours=1)

def test_replay_control():
    now = datetime.now()
    
    # Test play action
    control = ReplayControl(
        action="play",
        speed=1.5
    )
    assert control.action == "play"
    assert control.speed == 1.5
    assert control.position is None
    
    # Test pause action
    control = ReplayControl(action="pause")
    assert control.action == "pause"
    assert control.speed is None
    assert control.position is None
    
    # Test seek action
    control = ReplayControl(
        action="seek",
        position=now
    )
    assert control.action == "seek"
    assert control.position == now
    assert control.speed is None
    
    # Test with invalid action
    with pytest.raises(ValueError):
        ReplayControl(action="rewind")