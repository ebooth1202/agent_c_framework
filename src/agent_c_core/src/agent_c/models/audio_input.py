import base64
import logging
import mimetypes

from typing import Union
from pathlib import Path
from pydantic import Field, ConfigDict
from agent_c.models.base import BaseModel


class AudioInput(BaseModel):
    """
    A model to handle audio input for completion calls

    Attributes:
        format (str): The type of audio content (e.g., 'wav').
        content (Union[str, None]): A base64-encoded string representing the audio data.
    """
    format: str = Field("wav")
    content: Union[str, None] = None

    @classmethod
    def from_bytes(cls, audio_bytes: bytes, format_str: str = 'wav') -> "AudioInput":
        """
        Create an AudioInput instance from audio bytes.

        Args:
            audio_bytes: The audio content as bytes
            format_str: The format of the audio content (e.g., 'wav')

        Returns:
            AudioInput: An instance with the audio content base64 encoded
        """
        content = base64.b64encode(audio_bytes).decode('utf-8')
        return cls(format=format_str, content=content)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "AudioInput":
        """
        Create an AudioInput instance from a WAV or MP3 file.

        Args:
            file_path: Path to the audio file (WAV or MP3)

        Returns:
            AudioInput: An instance with the file's content base64 encoded

        Raises:
            ValueError: If the file format is not supported or file doesn't exist
            IOError: If there are issues reading the file
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Get the file format
        mime_type = mimetypes.guess_type(path)[0]
        if mime_type not in ('audio/wav', 'audio/x-wav', 'audio/mpeg', 'audio/mp3'):
            raise ValueError(f"Unsupported audio format: {mime_type}. Only WAV and MP3 are supported.")

        try:
            with path.open('rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
        except IOError as e:
            logging.error(f"Error reading audio file {file_path}: {str(e)}")
            raise


        format_str = 'wav' if 'wav' in mime_type.lower() else 'mp3'
        return cls(format=format_str, content=content)
