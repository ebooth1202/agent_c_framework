"""
HeyGen Streaming Avatar API models.

This package contains Pydantic models for the HeyGen Streaming Avatar API,
organized by functional areas.
"""

from .avatar import Avatar
from .session import (
    HeygenAvatarSessionData,
    ActiveSession,
    HistoricalSession,
)
from .requests import (
    NewSessionRequest,
    VoiceSettings,
    STTSettings,
    ElevenlabsSettings,
    SendTaskRequest,
    SessionIdRequest,
)
from .responses import (
    HeyGenBaseResponse,
    ListAvatarsResponse,
    NewSessionResponse,
    ListActiveSessionsResponse,
    ListHistoricalSessionsResponse,
    SendTaskResponse,
    CreateSessionTokenResponse,
    SessionTokenData,
    SimpleStatusResponse,
)

__all__ = [
    # Avatar models
    "Avatar",
    
    # Session models
    "HeygenAvatarSessionData",
    "ActiveSession", 
    "HistoricalSession",
    
    # Request models
    "NewSessionRequest",
    "VoiceSettings",
    "STTSettings", 
    "ElevenlabsSettings",
    "SendTaskRequest",
    "SessionIdRequest",
    
    # Response models
    "HeyGenBaseResponse",
    "ListAvatarsResponse",
    "NewSessionResponse",
    "ListActiveSessionsResponse",
    "ListHistoricalSessionsResponse",
    "SendTaskResponse",
    "CreateSessionTokenResponse",
    "SessionTokenData",
    "SimpleStatusResponse",
]