"""
Request models for HeyGen Streaming Avatar API.
"""

from typing import Optional, Dict, Any
from pydantic import Field

from agent_c.models.base import BaseModel


class ElevenlabsSettings(BaseModel):
    """Voice settings for ElevenLabs voice provider."""
    
    stability: Optional[float] = 0.75
    model_id: Optional[str] = "eleven_flash_v2_5"
    similarity_boost: Optional[float] = 0.75
    style: Optional[float] = 0.0
    use_speaker_boost: Optional[bool] = True


class VoiceSettings(BaseModel):
    """Voice configuration for streaming avatar."""
    
    voice_id: Optional[str] = None
    rate: Optional[float] = 1.0
    emotion: Optional[str] = None
    elevenlabs_settings: Optional[ElevenlabsSettings] = None


class STTSettings(BaseModel):
    """Speech-to-text configuration settings."""
    
    provider: Optional[str] = "assembly_ai"
    confidence: Optional[float] = 0.55


class NewSessionRequest(BaseModel):
    """Request model for creating a new streaming session."""
    
    quality: Optional[str] = "medium"
    avatar_id: Optional[str] = "default"
    voice: Optional[VoiceSettings] = None
    voice_name: Optional[str] = None
    stt_settings: Optional[STTSettings] = None
    video_encoding: Optional[str] = "VP8"
    knowledge_base: Optional[str] = None
    version: Optional[str] = None
    knowledge_base_id: Optional[str] = None
    disable_idle_timeout: Optional[bool] = False
    activity_idle_timeout: Optional[int] = 120


class SendTaskRequest(BaseModel):
    """Request model for sending a task to an avatar."""
    
    session_id: str
    text: str
    task_mode: Optional[str] = "sync"
    task_type: Optional[str] = "repeat"


class SessionIdRequest(BaseModel):
    """Base request model for operations requiring only a session ID."""
    
    session_id: str