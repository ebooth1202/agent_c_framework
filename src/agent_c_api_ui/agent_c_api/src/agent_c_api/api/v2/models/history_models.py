# src/agent_c_api/api/v2/models/history_models.py
from typing import Dict, List, Optional, Any, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

# Import core event models
from agent_c.models.events.base import BaseEvent
from agent_c.models.events.session_event import SessionEvent
from agent_c.models.events.chat import (
    InteractionEvent, CompletionEvent, MessageEvent, 
    SystemMessageEvent, TextDeltaEvent, ThoughtDeltaEvent,
    HistoryEvent
)
from agent_c.models.events.tool_calls import ToolCallEvent, ToolCallDeltaEvent

from .chat_models import ChatMessage, ChatEventUnion

class HistorySummary(BaseModel):
    """Summary of a recorded session history"""
    session_id: UUID = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    message_count: int = Field(..., description="Number of messages")
    duration: int = Field(..., description="Session duration in seconds")

class HistoryDetail(HistorySummary):
    """Detailed information about a session history"""
    files: List[str] = Field(..., description="List of log files for the session")
    event_types: Dict[str, int] = Field(..., description="Count of each event type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")
    user_id: Optional[str] = Field(None, description="User ID associated with the session")
    has_thinking: bool = Field(False, description="Whether the session includes thinking events")
    tool_calls: List[str] = Field([], description="List of tools used in the session")

class PaginationParams(BaseModel):
    """Parameters for pagination"""
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("start_time", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc or desc)")

class HistoryListResponse(BaseModel):
    """Response for listing session histories"""
    items: List[HistorySummary] = Field(..., description="List of session histories")
    total: int = Field(..., description="Total number of session histories")
    limit: int = Field(..., description="Maximum number of results returned")
    offset: int = Field(..., description="Number of results skipped")

class EventFilter(BaseModel):
    """Parameters for filtering history events"""
    event_types: Optional[List[str]] = Field(None, description="Event types to include")
    start_time: Optional[datetime] = Field(None, description="Start time for events")
    end_time: Optional[datetime] = Field(None, description="End time for events")
    limit: int = Field(100, description="Maximum number of events to return")

# We'll use the core event models directly (ChatEventUnion) instead of defining our own Event class
# This type alias covers all possible event types coming from stored history
HistoryEventUnion = ChatEventUnion

# For backwards compatibility with existing endpoint documentation
class StoredEvent(BaseModel):
    """
    A wrapper around core event models with additional metadata
    Used for stored events in history, primarily for documentation purposes
    """
    id: str = Field(..., description="Event ID")
    event: HistoryEventUnion = Field(..., description="The actual event data")
    timestamp: datetime = Field(..., description="Event timestamp")

class ReplayStatus(BaseModel):
    """Status of a session replay"""
    session_id: UUID = Field(..., description="Session ID")
    is_playing: bool = Field(..., description="Whether replay is playing")
    current_position: datetime = Field(..., description="Current replay position")
    start_time: datetime = Field(..., description="Session start time")
    end_time: datetime = Field(..., description="Session end time")

class ReplayControl(BaseModel):
    """Parameters for controlling replay"""
    action: Literal["play", "pause", "seek"] = Field(..., description="Control action")
    position: Optional[datetime] = Field(None, description="Position to seek to (for seek action)")
    speed: Optional[float] = Field(None, description="Playback speed multiplier (for play action)")