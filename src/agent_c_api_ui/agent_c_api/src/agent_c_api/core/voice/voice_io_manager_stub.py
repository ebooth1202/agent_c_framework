"""
Temporary stub for VoiceIOManager to allow realtime API to work without the full voice pipeline.
This is a placeholder implementation that provides the same interface but doesn't actually process audio.
"""

from typing import TYPE_CHECKING, Optional
from agent_c.util.logging_utils import LoggingManager

if TYPE_CHECKING:
    from .models import AvailableVoiceModel
    from agent_c_api.core.realtime_bridge import RealtimeBridge
    from agent_c.models.events.chat import AudioInputDeltaEvent


class VoiceIOManager:
    """
    Stub implementation of VoiceIOManager that provides the same interface
    but doesn't actually process audio. This allows the realtime API to work
    without the full voice pipeline implementation.
    """
    
    def __init__(self, bridge: "RealtimeBridge", voice: Optional['AvailableVoiceModel'] = None):
        self.logger = LoggingManager(__name__).get_logger()
        self._bridge = bridge
        self._voice: Optional['AvailableVoiceModel'] = voice
        self.logger.info("VoiceIOManager stub initialized - audio processing disabled")

    @property
    def is_running(self) -> bool:
        """
        Check if the voice pipeline is currently running.
        
        Returns:
            bool: Always False in stub implementation
        """
        return False

    def change_voice(self, voice: 'AvailableVoiceModel'):
        """
        Change the TTS voice model used in the pipeline.
        
        Args:
            voice (AvailableVoiceModel): The new voice model to use
        """
        self.logger.info(f"VoiceIOManager stub: Voice changed to {voice.voice_id} (no-op)")
        self._voice = voice

    def start(self, voice: Optional['AvailableVoiceModel'] = None, language: Optional[str] = None):
        """
        Start the voice pipeline to process audio input and generate responses.
        
        Args:
            voice (Optional[AvailableVoiceModel]): Voice model to use
            language (Optional[str]): Language setting
        """
        voice = voice or self._voice
        self.logger.info(f"VoiceIOManager stub: Start called with voice {voice.voice_id if voice else 'none'} (no-op)")

    def add_audio_delta(self, audio_delta: 'AudioInputDeltaEvent'):
        """
        Add an audio chunk to the input stream for processing.
        
        Args:
            audio_delta (AudioInputDeltaEvent): The incoming audio data chunk
        """
        self.logger.debug("VoiceIOManager stub: Audio delta received (ignored)")

    def add_audio(self, audio_delta: bytes):
        """
        Add an audio chunk to the input stream for processing.
        
        Args:
            audio_delta (bytes): The incoming audio data chunk
        """
        self.logger.debug("VoiceIOManager stub: Audio chunk received (ignored)")

    def close(self):
        """
        Close the voice pipeline and clean up resources.
        """
        self.logger.info("VoiceIOManager stub: Close called (no-op)")