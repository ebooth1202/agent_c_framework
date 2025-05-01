import pytest
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, List, Any

from agent_c_api.api.v2.models.history_models import (
    HistorySummary, HistoryDetail, PaginationParams, 
    HistoryListResponse, Event, EventFilter, 
    ReplayStatus, ReplayControl
)

def test_history_models_imports():
    """Verify that history models can be imported correctly from the centralized location"""
    # This test just verifies imports work, so we don't need to do anything else
    pass

def test_history_model_creation():
    """Test that models can be instantiated properly"""
    test_uuid = uuid4()
    now = datetime.now()
    
    # Test HistorySummary
    summary = HistorySummary(
        session_id=test_uuid,
        name="Test Session",
        created_at=now,
        updated_at=now,
        message_count=5,
        duration=300
    )
    assert summary.session_id == test_uuid
    assert summary.name == "Test Session"
    
    # Test Event
    event = Event(
        id="test-event-1",
        session_id=test_uuid,
        timestamp=now,
        event_type="message",
        data={"content": "Hello world"}
    )
    assert event.id == "test-event-1"
    assert event.session_id == test_uuid
    assert event.event_type == "message"
    
    # Test EventFilter
    filter_params = EventFilter(
        event_types=["message", "thinking"],
        start_time=now,
        end_time=now,
        limit=50
    )
    assert filter_params.event_types == ["message", "thinking"]
    assert filter_params.limit == 50