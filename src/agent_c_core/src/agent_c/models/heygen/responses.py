"""
Response models for HeyGen Streaming Avatar API.
"""

from typing import Optional, List, Dict, Any

from agent_c.models.base import BaseModel
from .avatar import Avatar
from .session import HeygenAvatarSessionData, ActiveSession, HistoricalSession


class HeyGenBaseResponse(BaseModel):
    """Base response model for HeyGen API responses."""
    
    code: int
    message: str


class ListAvatarsResponse(HeyGenBaseResponse):
    """Response model for listing avatars."""
    
    data: List[Avatar]


class NewSessionResponse(HeyGenBaseResponse):
    """Response model for creating a new session."""
    
    data: HeygenAvatarSessionData


class ActiveSessionsData(BaseModel):
    """Data container for active sessions."""
    
    sessions: List[ActiveSession]


class ListActiveSessionsResponse(HeyGenBaseResponse):
    """Response model for listing active sessions."""
    
    data: ActiveSessionsData


class ListHistoricalSessionsResponse(HeyGenBaseResponse):
    """Response model for listing historical sessions with pagination."""
    
    data: List[HistoricalSession]
    total: int
    page: int
    page_size: int
    next_pagination_token: Optional[str] = None


class SendTaskResponseData(BaseModel):
    """Data model for send task response."""
    
    duration_ms: float
    task_id: str


class SendTaskResponse(HeyGenBaseResponse):
    """Response model for sending a task."""
    
    data: SendTaskResponseData


class SessionTokenData(BaseModel):
    """Model representing session token data."""
    
    token: str


class CreateSessionTokenResponse(BaseModel):
    """Response model for creating session token."""
    
    error: Optional[str] = None
    data: SessionTokenData


class SimpleStatusResponse(HeyGenBaseResponse):
    """Simple response model for operations that return just status."""
    
    status: Optional[str] = None