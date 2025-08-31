"""
Session-related models for HeyGen Streaming Avatar API.
"""

from typing import Optional, List, Dict, Any

from agent_c.models.base import BaseModel


class HeygenAvatarSessionData(BaseModel):
    """Model representing session data from new session creation."""
    
    session_id: str
    url: str
    access_token: str
    session_duration_limit: int
    is_paid: bool
    realtime_endpoint: str
    sdp: Optional[str] = None
    ice_servers: Optional[List[Dict[str, Any]]] = None
    ice_servers2: Optional[List[Dict[str, Any]]] = None


class ActiveSession(BaseModel):
    """Model representing an active streaming session."""
    
    session_id: str
    status: str
    created_at: int
    api_key_type: str


class HistoricalSession(BaseModel):
    """Model representing a historical streaming session."""
    
    session_id: str
    status: str
    created_at: int
    api_key_type: str
    duration: int
    avatar_id: str
    voice_name: str