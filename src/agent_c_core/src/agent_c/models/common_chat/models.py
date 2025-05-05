from enum import Enum
from typing import List, Optional, Dict, Any, Union, Literal, Annotated
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict, field_validator


class MessageRole(str, Enum):
    """Common enumeration of message roles across providers."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"  # For tool/function responses


class ContentBlockType(str, Enum):
    """Enumeration of content block types supported in the common model."""
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    THINKING = "thinking"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"


class BaseContentBlock(BaseModel):
    """Base class for all content blocks."""
    type: ContentBlockType
    
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True
    )


class TextContentBlock(BaseContentBlock):
    """A block of text content."""
    type: Literal[ContentBlockType.TEXT] = ContentBlockType.TEXT
    text: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)


class ToolUseContentBlock(BaseContentBlock):
    """A block representing a tool call."""
    type: Literal[ContentBlockType.TOOL_USE] = ContentBlockType.TOOL_USE
    tool_name: str
    tool_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolResultContentBlock(BaseContentBlock):
    """A block representing a tool call result."""
    type: Literal[ContentBlockType.TOOL_RESULT] = ContentBlockType.TOOL_RESULT
    tool_name: str
    tool_id: str
    result: Any


class ThinkingContentBlock(BaseContentBlock):
    """A block of thinking/reasoning content."""
    type: Literal[ContentBlockType.THINKING] = ContentBlockType.THINKING
    thought: str
    redacted: bool = False


class ImageContentBlock(BaseContentBlock):
    """A block containing an image."""
    type: Literal[ContentBlockType.IMAGE] = ContentBlockType.IMAGE
    source: Dict[str, Any]  # Could be URL, base64, etc.


class AudioContentBlock(BaseContentBlock):
    """A block containing audio data."""
    type: Literal[ContentBlockType.AUDIO] = ContentBlockType.AUDIO
    source: Dict[str, Any]  # Could be URL, base64, etc.


# Define a discriminated union of content block types
ContentBlock = Annotated[
    Union[
        TextContentBlock, 
        ToolUseContentBlock,
        ToolResultContentBlock,
        ThinkingContentBlock,
        ImageContentBlock,
        AudioContentBlock
    ],
    Field(discriminator="type")
]


class StopInfo(BaseModel):
    """Information about why a message generation stopped."""
    reason: str  # end_turn, max_tokens, stop_sequence, tool_use, etc.
    details: Optional[Dict[str, Any]] = None


class TokenUsage(BaseModel):
    """Token usage information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class ProviderMetadata(BaseModel):
    """Provider-specific metadata."""
    provider_name: str  # "anthropic", "openai", etc.
    raw_message: Dict[str, Any]  # The raw message from the provider
    model: str  # The model used to generate this message
    stop_info: Optional[StopInfo] = None
    usage: Optional[TokenUsage] = None
    # Any other provider-specific fields
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class CommonChatMessage(BaseModel):
    """A common message format that can represent messages from different providers.
    
    This model provides a consistent interface for working with messages from 
    different AI providers like OpenAI and Anthropic.
    """
    id: str = Field(description="Unique ID for this message")
    role: MessageRole = Field(description="The role of this message (user, assistant, system, tool)")
    content: List[ContentBlock] = Field(description="Content blocks for this message")
    created_at: datetime = Field(description="When this message was created")
    provider_metadata: Optional[ProviderMetadata] = Field(
        default=None, description="Provider-specific metadata"
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "msg_123456",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Hello, how can I help you today?"
                        }
                    ],
                    "created_at": "2023-08-01T12:00:00Z"
                }
            ]
        }
    )
    
    @field_validator('id', mode='before')
    @classmethod
    def set_id_if_empty(cls, v):
        """Set a UUID if id is not provided."""
        if not v:
            return str(uuid4())
        return v

    @field_validator('created_at', mode='before')
    @classmethod
    def set_created_at_if_empty(cls, v):
        """Set current time if created_at is not provided."""
        if not v:
            return datetime.now()
        return v
    
    @property
    def text_content(self) -> str:
        """Get all text content concatenated together."""
        return ''.join([
            block.text for block in self.content 
            if isinstance(block, TextContentBlock)
        ])
    
    def get_content_by_type(self, content_type: ContentBlockType) -> List[ContentBlock]:
        """Get all content blocks of a specific type."""
        return [block for block in self.content if block.type == content_type]