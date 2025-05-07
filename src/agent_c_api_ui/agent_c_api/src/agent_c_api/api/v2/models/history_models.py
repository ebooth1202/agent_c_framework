# src/agent_c_api/api/v2/models/history_models.py
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
# Removed UUID import as it's no longer needed

from .chat_models import ChatEventUnion

class HistorySummary(BaseModel):
    """
    Summary of a recorded session history
    
    Contains key information about a session's history including identifiers,
    timestamps, and basic metrics like message count and duration.
    """
    session_id: str = Field(
        ..., 
        description="Unique session identifier in MnemonicSlug format (e.g., 'tiger-castle')"
    )
    name: str = Field(
        ..., 
        description="Human-readable session name"
    )
    created_at: datetime = Field(
        ..., 
        description="Timestamp when the session was created"
    )
    updated_at: datetime = Field(
        ..., 
        description="Timestamp when the session was last updated"
    )
    message_count: int = Field(
        ..., 
        description="Total number of message events in the session"
    )
    duration: int = Field(
        ..., 
        description="Total duration of the session in seconds"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "tiger-castle",
                "name": "Task Planning Session",
                "created_at": "2025-04-01T14:30:00Z",
                "updated_at": "2025-04-01T15:45:00Z",
                "message_count": 24,
                "duration": 4500
            }
        }
    }

class HistoryDetail(HistorySummary):
    """
    Detailed information about a session history
    
    Extends HistorySummary with additional information about the session's
    contents, including file records, event types, and analysis metadata.
    This provides a richer view of the session's contents without requiring
    full event retrieval.
    """
    files: List[str] = Field(
        ..., 
        description="List of log filenames containing the session's events"
    )
    event_types: Dict[str, int] = Field(
        ..., 
        description="Count of each event type in the session (e.g. 'text_delta': 80)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional session metadata such as model information"
    )
    user_id: Optional[str] = Field(
        None, 
        description="Identifier of the user who created this session"
    )
    has_thinking: bool = Field(
        False, 
        description="Whether the session includes thinking events (agent reasoning)"
    )
    tool_calls: List[str] = Field(
        [], 
        description="List of tool names that were called during the session"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "session_id": "tiger-castle",
                "name": "Task Planning Session",
                "created_at": "2025-04-01T14:30:00Z",
                "updated_at": "2025-04-01T15:45:00Z",
                "message_count": 24,
                "duration": 4500,
                "files": ["events_tiger-castle_1.jsonl", "events_tiger-castle_2.jsonl"],
                "event_types": {
                    "text_delta": 120,
                    "tool_call": 15,
                    "user_request": 12,
                    "thinking": 30
                },
                "metadata": {
                    "model": "gpt-4-turbo",
                    "completion_tokens": 4820,
                    "prompt_tokens": 1650
                },
                "user_id": "user_12345",
                "has_thinking": True,
                "tool_calls": ["web_search", "file_reader", "code_interpreter"]
            }
        })


class PaginationParams(BaseModel):
    """
    Parameters for pagination
    
    Defines common pagination parameters used across various list endpoints
    for controlling result set size and ordering.
    """
    limit: int = Field(
        50, 
        ge=1, 
        le=100, 
        description="Maximum number of results to return (1-100)"
    )
    offset: int = Field(
        0, 
        ge=0, 
        description="Number of results to skip before returning results"
    )
    sort_by: str = Field(
        "start_time", 
        description="Field name to sort results by (e.g., 'start_time', 'name')"
    )
    sort_order: str = Field(
        "desc", 
        description="Sort direction, either 'asc' (ascending) or 'desc' (descending)"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "limit": 20,
                "offset": 40,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        })

class HistoryListResponse(BaseModel):
    """
    Response for listing session histories
    
    Provides paginated access to session history summaries along with pagination metadata.
    """
    items: List[HistorySummary] = Field(
        ..., 
        description="List of session history summaries matching the query criteria"
    )
    total: int = Field(
        ..., 
        description="Total number of session histories available (across all pages)"
    )
    limit: int = Field(
        ..., 
        description="Maximum number of results returned in this response"
    )
    offset: int = Field(
        ..., 
        description="Number of results skipped before this page"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "items": [
                    {
                        "session_id": "tiger-castle",
                        "name": "Task Planning Session",
                        "created_at": "2025-04-01T14:30:00Z",
                        "updated_at": "2025-04-01T15:45:00Z",
                        "message_count": 24,
                        "duration": 4500
                    },
                    {
                        "session_id": "apollo-banana",
                        "name": "Code Review Session",
                        "created_at": "2025-04-02T09:15:00Z",
                        "updated_at": "2025-04-02T10:30:00Z",
                        "message_count": 18,
                        "duration": 4200
                    }
                ],
                "total": 42,
                "limit": 20,
                "offset": 0
            }
        })


class EventFilter(BaseModel):
    """
    Parameters for filtering history events
    
    Provides flexible options for filtering session event history by type,
    time range, and limiting the result set size. Used primarily with the
    events retrieval endpoints.
    """
    event_types: Optional[List[str]] = Field(
        None, 
        description="List of event type names to include (e.g., 'text_delta', 'tool_call', 'thinking')"
    )
    start_time: Optional[datetime] = Field(
        None, 
        description="Only include events occurring at or after this timestamp"
    )
    end_time: Optional[datetime] = Field(
        None, 
        description="Only include events occurring at or before this timestamp"
    )
    limit: int = Field(
        100, 
        ge=1, 
        le=1000,
        description="Maximum number of events to return (1-1000)"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "examples": [
                # Example 1: Filtering by event type
                {
                    "event_types": ["tool_call", "thinking"],
                    "limit": 50
                },
                # Example 2: Filtering by time range
                {
                    "start_time": "2025-04-01T14:45:00Z",
                    "end_time": "2025-04-01T15:15:00Z",
                    "limit": 200
                },
                # Example 3: Combined filtering
                {
                    "event_types": ["user_request", "completion_event"],
                    "start_time": "2025-04-01T14:30:00Z",
                    "limit": 100
                }
            ]
        })


# We'll use the core event models directly (ChatEventUnion) instead of defining our own Event class
# This type alias covers all possible event types coming from stored history
HistoryEventUnion = ChatEventUnion

# For backwards compatibility with existing endpoint documentation
class StoredEvent(BaseModel):
    """
    A wrapper around core event models with additional metadata
    
    Provides a standardized container for history events with consistent metadata,
    regardless of the specific event type. This allows for uniform handling
    across different event types while preserving the type-specific data.
    """
    id: str = Field(
        ..., 
        description="Unique identifier for the event record"
    )
    event: HistoryEventUnion = Field(
        ..., 
        description="The actual event data containing type-specific fields"
    )
    timestamp: datetime = Field(
        ..., 
        description="When this event occurred in the session timeline"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "examples": [
                # Example of a user message event
                {
                    "id": "evt_1234567890",
                    "timestamp": "2025-04-01T14:32:15Z",
                    "event": {
                        "event_type": "message",
                        "role": "user",
                        "content": "Can you help me analyze this dataset?",
                        "message_id": "msg_abcdef123456"
                    }
                },
                # Example of a tool call event
                {
                    "id": "evt_0987654321",
                    "timestamp": "2025-04-01T14:35:42Z",
                    "event": {
                        "event_type": "tool_call",
                        "tool_name": "data_analysis",
                        "input": {
                            "file_path": "data.csv",
                            "operation": "summary_statistics"
                        },
                        "call_id": "call_defabc456789"
                    }
                },
                # Example of a thinking event
                {
                    "id": "evt_5678901234",
                    "timestamp": "2025-04-01T14:33:10Z",
                    "event": {
                        "event_type": "thinking",
                        "content": "I should first check what format the dataset is in, then determine appropriate analysis methods.",
                        "thinking_id": "think_987654abcdef"
                    }
                }
            ]
        })

class ReplayStatus(BaseModel):
    """
    Status of a session replay
    
    Provides information about the current state of a session replay,
    including playback status and position information. Used to track
    and control session replay functionality.
    """
    session_id: str = Field(
        ..., 
        description="Unique session identifier in MnemonicSlug format (e.g., 'tiger-castle')"
    )
    is_playing: bool = Field(
        ..., 
        description="Whether the replay is currently playing (true) or paused (false)"
    )
    current_position: datetime = Field(
        ..., 
        description="Current timestamp position in the replay timeline"
    )
    start_time: datetime = Field(
        ..., 
        description="Timestamp of the first event in the session"
    )
    end_time: datetime = Field(
        ..., 
        description="Timestamp of the last event in the session"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "session_id": "tiger-castle",
                "is_playing": True,
                "current_position": "2025-04-01T14:40:15Z",
                "start_time": "2025-04-01T14:30:00Z",
                "end_time": "2025-04-01T15:45:00Z"
            }
        }
    )

class ReplayControl(BaseModel):
    """
    Parameters for controlling replay
    
    Defines the available actions and parameters for controlling a session replay.
    Supports actions like play, pause, and seeking to specific positions in the timeline.
    """
    action: Literal["play", "pause", "seek"] = Field(
        ..., 
        description="Control action to perform on the replay ('play', 'pause', or 'seek')"
    )
    position: Optional[datetime] = Field(
        None, 
        description="Target timestamp position to seek to (required when action is 'seek')"
    )
    speed: Optional[float] = Field(
        None, 
        ge=0.1, 
        le=10.0,
        description="Playback speed multiplier (0.1-10.0, where 1.0 is normal speed)"
    )
    
    model_config = ConfigDict(
        json_schema_extra= {
            "examples": [
                # Example 1: Start playback at normal speed
                {
                    "action": "play",
                    "speed": 1.0
                },
                # Example 2: Start playback at 2x speed
                {
                    "action": "play",
                    "speed": 2.0
                },
                # Example 3: Pause playback
                {
                    "action": "pause"
                },
                # Example 4: Seek to a specific position
                {
                    "action": "seek",
                    "position": "2025-04-01T14:35:00Z"
                }
            ]
        })