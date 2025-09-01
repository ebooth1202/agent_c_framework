"""
Avatar-related models for HeyGen Streaming Avatar API.
"""

from agent_c.models.base import BaseModel


class Avatar(BaseModel):
    """Model representing a HeyGen streaming avatar."""
    
    avatar_id: str
    created_at: int
    default_voice: str
    is_public: bool
    normal_preview: str
    pose_name: str
    status: str