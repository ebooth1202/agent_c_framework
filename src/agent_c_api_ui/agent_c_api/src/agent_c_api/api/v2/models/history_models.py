# src/agent_c_api/api/v2/models/history_models.py
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from .chat_models import ChatMessage

class HistorySummary(BaseModel):
    """Summary of a recorded session history"""
    session_id: UUID = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    message_count: int = Field(..., description="Number of messages")
    duration: int = Field(..., description="Session duration in seconds")

class EventFilter(BaseModel):
    """Parameters for filtering history events"""
    event_types: Optional[List[str]] = Field(None, description="Event types to include")
    start_time: Optional[datetime] = Field(None, description="Start time for events")
    end_time: Optional[datetime] = Field(None, description="End time for events")
    limit: int = Field(100, description="Maximum number of events to return")

class Event(BaseModel):
    """A recorded event in session history"""
    id: str = Field(..., description="Event ID")
    session_id: UUID = Field(..., description="Session ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")

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