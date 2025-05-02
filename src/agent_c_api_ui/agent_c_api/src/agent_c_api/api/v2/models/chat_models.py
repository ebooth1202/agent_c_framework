# src/agent_c_api/api/v2/models/chat_models.py
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from uuid import UUID

from .tool_models import ToolCall, ToolResult

class ChatMessageContent(BaseModel):
    """Content of a chat message"""
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

class ChatMessage(BaseModel):
    """A message in a chat conversation"""
    id: Optional[UUID] = Field(None, description="Message ID")
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    content: List[ChatMessageContent] = Field(..., description="Message content parts")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls made by assistant")
    tool_results: Optional[List[ToolResult]] = Field(None, description="Results of tool calls")

class ChatRequest(BaseModel):
    """A request to send a chat message"""
    message: ChatMessage = Field(..., description="Message to send")
    stream: bool = Field(True, description="Whether to stream the response")

class ChatEventType(str, Enum):
    """Types of events during a chat interaction"""
    MESSAGE_START = "message_start"
    MESSAGE_TEXT = "message_text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    MESSAGE_END = "message_end"
    ERROR = "error"

class ChatEvent(BaseModel):
    """A streaming event during chat"""
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(..., description="Event timestamp")