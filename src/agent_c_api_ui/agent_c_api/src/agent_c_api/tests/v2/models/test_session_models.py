# src/agent_c_api/tests/v2/models/test_session_models.py
import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from agent_c_api.api.v2.models.session_models import (
    SessionCreate, SessionSummary, SessionDetail, SessionUpdate
)

def test_session_create_model():
    # Test with minimal fields
    session = SessionCreate()
    assert session.name is None
    assert session.model_id is None
    assert session.persona_id is None
    assert session.tool_ids is None
    assert session.metadata is None
    
    # Test with all fields
    session = SessionCreate(
        name="Test Session",
        model_id="gpt-4",
        persona_id="default",
        tool_ids=["calculator", "weather"],
        metadata={"created_by": "test"}
    )
    assert session.name == "Test Session"
    assert session.model_id == "gpt-4"
    assert session.persona_id == "default"
    assert session.tool_ids == ["calculator", "weather"]
    assert session.metadata == {"created_by": "test"}

def test_session_summary_model():
    now = datetime.now()
    session_id = uuid4()
    
    # Test creating a valid summary
    summary = SessionSummary(
        id=session_id,
        name="Test Session",
        created_at=now,
        updated_at=now,
        model_id="gpt-4",
        persona_id="default",
        is_active=True
    )
    
    assert summary.id == session_id
    assert summary.name == "Test Session"
    assert summary.created_at == now
    assert summary.updated_at == now
    assert summary.model_id == "gpt-4"
    assert summary.persona_id == "default"
    assert summary.is_active is True

def test_session_detail_model():
    now = datetime.now()
    session_id = uuid4()
    
    # Test creating a valid detail object
    detail = SessionDetail(
        id=session_id,
        name="Test Session",
        created_at=now,
        updated_at=now,
        model_id="gpt-4",
        persona_id="default",
        is_active=True,
        tool_ids=["calculator", "weather"],
        metadata={"created_by": "test"},
        message_count=5
    )
    
    assert detail.id == session_id
    assert detail.name == "Test Session"
    assert detail.tool_ids == ["calculator", "weather"]
    assert detail.metadata == {"created_by": "test"}
    assert detail.message_count == 5

def test_session_update_model():
    # Test with no fields (valid but does nothing)
    update = SessionUpdate()
    assert update.name is None
    assert update.metadata is None
    
    # Test with all fields
    update = SessionUpdate(
        name="Updated Name",
        metadata={"updated": True}
    )
    assert update.name == "Updated Name"
    assert update.metadata == {"updated": True}