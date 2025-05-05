# src/agent_c_api/api/v2/models/chat_models.py
from typing import  List, Optional,  Literal, Union, ClassVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID

# Import core event models
from agent_c.models.events.chat import (
    InteractionEvent, CompletionEvent, MessageEvent, 
    SystemMessageEvent, TextDeltaEvent, ThoughtDeltaEvent,
    HistoryEvent
)
from agent_c.models.events.tool_calls import ToolCallEvent, ToolCallDeltaEvent

# Import core content block models
from agent_c.models.common_chat import TextContentBlock as TextBlock, ImageContentBlock as ImageBlock, BaseContentBlock
class FileBlock(BaseContentBlock):
    """Placeholder for file content blocks"""
    file_id: str
    mime_type: Optional[str] = None

from .tool_models import ToolCall, ToolResult

# Type alias for all possible event types
ChatEventUnion = Union[
    InteractionEvent, CompletionEvent, MessageEvent, 
    SystemMessageEvent, TextDeltaEvent, ThoughtDeltaEvent,
    HistoryEvent, ToolCallEvent, ToolCallDeltaEvent
]

# Type alias for all possible content block types
ContentBlockUnion = Union[TextBlock, FileBlock, ImageBlock]

# For backward compatibility and API stability, we'll keep the ChatMessageContent
# model but update it to be a wrapper around core content blocks
class ChatMessageContent(BaseModel):
    """Content of a chat message using core content blocks
    
    This model represents the different types of content that can be included in a chat message,
    such as text, images, or file attachments. It provides a structured way to handle
    multimodal messages in the chat API.
    """
    type: Literal["text", "image", "file"] = Field(
        ..., 
        description="Content type (text, image, or file)"
    )
    text: Optional[str] = Field(
        None, 
        description="Text content when type is 'text'"
    )
    file_id: Optional[str] = Field(
        None, 
        description="File ID for file content when type is 'image' or 'file'"
    )
    mime_type: Optional[str] = Field(
        None, 
        description="MIME type for file content (e.g., 'image/jpeg', 'application/pdf')"
    )
    
    model_config = ConfigDict(
        json_schema_extra = {
            "examples": [
                {
                    "type": "text",
                    "text": "Hello, can you help me with a Python question?"
                },
                {
                    "type": "image",
                    "file_id": "f8d7e91c-3f6a-4b1d-8d2e-1a7bb6f5abcd",
                    "mime_type": "image/jpeg"
                },
                {
                    "type": "file",
                    "file_id": "a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5cde",
                    "mime_type": "application/pdf"
                }
            ]
        }
    )
    
    @classmethod
    @field_validator('text')
    def text_required_for_text_type(cls, v: Optional[str], info) -> Optional[str]:
        if info.data.get('type') == 'text' and v is None:
            raise ValueError('text is required when type is text')
        return v
        
    @classmethod
    @field_validator('file_id')
    def file_id_required_for_file_types(cls, v: Optional[str], info) -> Optional[str]:
        if info.data.get('type') in ['image', 'file'] and v is None:
            raise ValueError('file_id is required when type is image or file')
        return v
        
    def to_content_block(self) -> ContentBlockUnion:
        """Convert to a core content block"""
        if self.type == "text":
            return TextBlock(text=self.text)
        elif self.type == "image":
            return ImageBlock(source={"file_id": self.file_id, "mime_type": self.mime_type})
        elif self.type == "file":
            return FileBlock(file_id=self.file_id, mime_type=self.mime_type)
        else:
            raise ValueError(f"Unknown content type: {self.type}")
    
    @classmethod
    def from_content_block(cls, block: ContentBlockUnion) -> "ChatMessageContent":
        """Create from a core content block"""
        if isinstance(block, TextBlock):
            return cls(type="text", text=block.text)
        elif isinstance(block, ImageBlock):
            source = block.source
            return cls(type="image", file_id=source.get("file_id"), mime_type=source.get("mime_type"))
        elif isinstance(block, FileBlock):
            return cls(type="file", file_id=block.file_id, mime_type=block.mime_type)
        else:
            raise ValueError(f"Unknown content block type: {type(block)}")

# Our main chat message model that uses the core MessageEvent model
class ChatMessage(BaseModel):
    """A message in a chat conversation
    
    Uses the core MessageEvent model internally while providing a consistent
    external API interface. This model serves as an adapter between the API and
    the core models.
    
    Each message can contain multiple content parts (text, images, files), tool calls
    made by the assistant, and the results of those tool calls. This structure enables
    rich, multimodal interactions between users and agents.
    """
    id: Optional[UUID] = Field(
        None, 
        description="Unique identifier for the message"
    )
    role: Literal["user", "assistant", "system"] = Field(
        ..., 
        description="Role of the message sender (user, assistant, or system)"
    )
    created_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when the message was created"
    )
    content: List[ChatMessageContent] = Field(
        ..., 
        description="List of content parts that make up the message (text, images, files)"
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        None, 
        description="List of tool calls initiated by the assistant during this message"
    )
    tool_results: Optional[List[ToolResult]] = Field(
        None, 
        description="Results returned from tool calls for this message"
    )
    
    model_config: ClassVar[dict] = {
        "json_schema_extra": {
            "examples": [
                # User message with text only
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "How do I read a file in Python?"
                        }
                    ]
                },
                # User message with text and image
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's wrong with this code?"
                        },
                        {
                            "type": "image",
                            "file_id": "f8d7e91c-3f6a-4b1d-8d2e-1a7bb6f5abcd",
                            "mime_type": "image/png"
                        }
                    ]
                },
                # Assistant message with text and tool call
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here's the current weather in Seattle:"
                        }
                    ],
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "name": "get_weather",
                            "arguments": {
                                "location": "Seattle",
                                "units": "imperial"
                            }
                        }
                    ],
                    "tool_results": [
                        {
                            "call_id": "call_abc123",
                            "result": {
                                "temperature": 72,
                                "condition": "sunny",
                                "humidity": 65
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    def to_message_event(self, session_id: str) -> MessageEvent:
        """Convert to a core MessageEvent
        
        Args:
            session_id: The session ID to associate with this message
            
        Returns:
            A MessageEvent instance from the core library
        """
        # For simple cases, assume text content is concatenated
        text_content = "\n".join([c.text for c in self.content if c.type == "text" and c.text])
        
        # Create the message event
        return MessageEvent(
            session_id=session_id,
            role=self.role,
            content=text_content,
            format="markdown",  # Default to markdown for now
            # We can add more metadata as needed
        )
    
    @classmethod
    def from_message_event(cls, event: MessageEvent) -> "ChatMessage":
        """Create from a core MessageEvent
        
        Args:
            event: A MessageEvent from the core library
            
        Returns:
            A ChatMessage instance for the API
        """
        # For simple cases, convert text content to a list with one item
        content = [ChatMessageContent(type="text", text=event.content)]
        
        # TODO: Handle more complex content blocks when needed
        
        return cls(
            role=event.role,
            content=content,
            # Convert timestamp if available
            created_at=event.timestamp if hasattr(event, 'timestamp') else None,
        )

class ChatRequest(BaseModel):
    """A request to send a chat message
    
    Contains the message to send to the agent and whether to stream the response.
    When streaming is enabled, the API returns a server-sent events (SSE) stream
    of response events. When disabled, the API returns a complete response once
    the interaction is finished.
    """
    message: ChatMessage = Field(
        ..., 
        description="The message to send to the agent"
    )
    stream: bool = Field(
        True, 
        description="Whether to stream the response as server-sent events (SSE)"
    )
    
    model_config: ClassVar[dict] = {
        "json_schema_extra": {
            "examples": [
                # Simple text message with streaming
                {
                    "message": {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What is the capital of France?"
                            }
                        ]
                    },
                    "stream": True
                },
                # Message with image attachment
                {
                    "message": {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Can you describe what's in this image?"
                            },
                            {
                                "type": "image",
                                "file_id": "f8d7e91c-3f6a-4b1d-8d2e-1a7bb6f5abcd"
                            }
                        ]
                    },
                    "stream": True
                }
            ]
        }
    }

class ChatResponse(BaseModel):
    """A response containing a chat message
    
    This model is used for non-streaming responses. It contains the complete message
    from the assistant along with a completion ID that can be used for reference.
    
    Note: Current API implementation primarily supports streaming responses. Non-streaming
    responses may be implemented in future versions.
    """
    message: ChatMessage = Field(
        ..., 
        description="The complete response message from the assistant"
    )
    completion_id: Optional[str] = Field(
        None, 
        description="Unique identifier for this completion (for reference and tracking)"
    )
    
    model_config: ClassVar[dict] = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": {
                        "id": "msg_123abc",
                        "role": "assistant",
                        "created_at": "2025-04-04T12:00:00Z",
                        "content": [
                            {
                                "type": "text",
                                "text": "Paris is the capital of France. It's known as the 'City of Light' and is famous for landmarks like the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral."
                            }
                        ]
                    },
                    "completion_id": "comp_xyz789"
                }
            ]
        }
    }

class ChatEventType(str, Enum):
    """
    Types of events during a chat interaction, aligned with core event types.
    
    This enum defines the possible event types that can occur during a streaming
    chat interaction. Each event type corresponds to a specific kind of update
    from the agent, such as text generation, tool usage, or thinking process.
    
    While the streaming API returns core event objects directly, this enum is useful
    for filtering events and understanding the event structure.
    """
    INTERACTION = "interaction"  # InteractionEvent
    COMPLETION = "completion"    # CompletionEvent
    MESSAGE = "message"        # MessageEvent/SystemMessageEvent
    TEXT_DELTA = "text_delta"  # TextDeltaEvent
    THOUGHT_DELTA = "thought_delta"  # ThoughtDeltaEvent
    TOOL_CALL = "tool_call"    # ToolCallEvent
    TOOL_CALL_DELTA = "tool_select_delta"  # ToolCallDeltaEvent
    HISTORY = "history"        # HistoryEvent
    
# ChatEvent is replaced by direct use of the core event models (ChatEventUnion type)
# The StreamingResponse will use these core event types directly