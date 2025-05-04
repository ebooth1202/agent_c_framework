# src/agent_c_api/api/v2/models/chat_models.py
from typing import Dict, List, Optional, Any, Literal, Union, ForwardRef
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID

# Import core event models
from agent_c.models.events.base import BaseEvent
from agent_c.models.events.session_event import SessionEvent, SemiSessionEvent
from agent_c.models.events.chat import (
    InteractionEvent, CompletionEvent, MessageEvent, 
    SystemMessageEvent, TextDeltaEvent, ThoughtDeltaEvent,
    HistoryEvent
)
from agent_c.models.events.tool_calls import ToolCallEvent, ToolCallDeltaEvent

# Import or placeholder for core content block models
from agent_c.models.content import ContentBlock, TextBlock, FileBlock, ImageBlock

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
    """Content of a chat message using core content blocks"""
    type: Literal["text", "image", "file"] = Field(..., description="Content type")
    text: Optional[str] = Field(None, description="Text content")
    file_id: Optional[str] = Field(None, description="File ID for file content")
    mime_type: Optional[str] = Field(None, description="MIME type for file content")
    
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
            return TextBlock(content=self.text)
        elif self.type == "image":
            return ImageBlock(file_id=self.file_id, mime_type=self.mime_type)
        elif self.type == "file":
            return FileBlock(file_id=self.file_id, mime_type=self.mime_type)
        else:
            raise ValueError(f"Unknown content type: {self.type}")
    
    @classmethod
    def from_content_block(cls, block: ContentBlockUnion) -> "ChatMessageContent":
        """Create from a core content block"""
        if isinstance(block, TextBlock):
            return cls(type="text", text=block.content)
        elif isinstance(block, ImageBlock):
            return cls(type="image", file_id=block.file_id, mime_type=block.mime_type)
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
    """
    id: Optional[UUID] = Field(None, description="Message ID")
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    content: List[ChatMessageContent] = Field(..., description="Message content parts")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls made by assistant")
    tool_results: Optional[List[ToolResult]] = Field(None, description="Results of tool calls")
    
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
    """A request to send a chat message"""
    message: ChatMessage = Field(..., description="Message to send")
    stream: bool = Field(True, description="Whether to stream the response")

class ChatResponse(BaseModel):
    """A response containing a chat message"""
    message: ChatMessage = Field(..., description="The response message")
    completion_id: Optional[str] = Field(None, description="Completion ID for reference")

class ChatEventType(str, Enum):
    """
    Types of events during a chat interaction, aligned with core event types.
    This enum can be used for filtering but the actual events use the core model types.
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