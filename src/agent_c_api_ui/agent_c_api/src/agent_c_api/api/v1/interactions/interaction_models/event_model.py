from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

class ReplayControlRequest(BaseModel):
    action: str  # play, pause, stop, seek
    position: Optional[str] = None  # timestamp to seek to

class EventType(str, Enum):
    SYSTEM_PROMPT = "system_prompt"
    COMPLETION_OPTIONS = "completion_options"
    INTERACTION = "interaction"
    COMPLETION = "completion"
    THOUGHT_DELTA = "thought_delta"
    TEXT_DELTA = "text_delta"
    TOOL_SELECT_DELTA = "tool_select_delta"
    TOOL_CALL = "tool_call"
    HISTORY = "history"
    USER_REQUEST = "user_request"
    RENDER_MEDIA = "render_media" # used by tool calls to emit events.

class Event(BaseModel):
    # whenever you do a model_dump here, ensure you do mode='json', so that datetime objects are serialized
    timestamp: datetime
    type: EventType
    session_id: Optional[str] = None
    role: Optional[str] = None
    content: Optional[Any] = None
    format: Optional[str] = None
    running: Optional[bool] = None
    active: Optional[bool] = None
    vendor: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    raw: Dict[str, Any]  # Original event data