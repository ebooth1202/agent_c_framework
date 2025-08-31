"""
Request models for HeyGen Streaming Avatar API.
"""

from typing import Optional, Dict, Any
from pydantic import Field

from agent_c.models.base import BaseModel


class ElevenlabsSettings(BaseModel):
    """Voice settings for ElevenLabs voice provider."""
    
    stability: Optional[float] = None
    model_id: Optional[str] = "eleven_flash_v2_5"
    similarity_boost: Optional[float] = None
    style: Optional[float] = None
    use_speaker_boost: Optional[bool] = None


class VoiceSettings(BaseModel):
    """Voice configuration for streaming avatar."""
    
    voice_id: Optional[str] = None
    rate: Optional[float] = 1.5
    emotion: Optional[str] = "excited"
    elevenlabs_settings: Optional[ElevenlabsSettings] = Field(default_factory=lambda: ElevenlabsSettings())


class STTSettings(BaseModel):
    """Speech-to-text configuration settings."""
    
    provider: Optional[str] = "deepgram"
    confidence: Optional[float] = None


class NewSessionRequest(BaseModel):
    """Request model for creating a new streaming session."""
    avatar_id: Optional[str] = None
    quality: Optional[str] = "medium"
    voice: Optional[VoiceSettings] = Field(default_factory=lambda: VoiceSettings())
    language: Optional[str] = "en"
    version: Optional[str] = "v2"
    video_encoding: Optional[str] = "H264"
    source: Optional[str] = "sdk"
    stt_settings: Optional[STTSettings] = Field(default_factory=lambda: STTSettings())
    ia_is_livekit_transport: Optional[bool] = False
    knowledge_base: Optional[str] = None
    knowledge_base_id: Optional[str] = None
    disable_idle_timeout: Optional[bool] = None
    activity_idle_timeout: Optional[int] = None



class SendTaskRequest(BaseModel):
    """Request model for sending a task to an avatar."""
    
    session_id: str
    text: str
    task_mode: Optional[str] = "sync"
    task_type: Optional[str] = "repeat"


class SessionIdRequest(BaseModel):
    """Base request model for operations requiring only a session ID."""
    
    session_id: str