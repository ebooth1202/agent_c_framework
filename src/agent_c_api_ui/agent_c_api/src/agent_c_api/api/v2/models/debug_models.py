# src/agent_c_api/api/v2/models/debug_models.py
from typing import List, Optional
from pydantic import BaseModel, Field


class MessagePreview(BaseModel):
    """Preview of a chat message in the session."""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content_preview: str = Field(..., description="Preview of the message content")
    timestamp: Optional[str] = Field(None, description="Timestamp when the message was sent")


class SessionManagerDebug(BaseModel):
    """Debug information about the session manager."""
    exists: bool = Field(..., description="Whether the session manager exists")
    user_id: Optional[str] = Field(None, description="User ID associated with the session")
    has_chat_session: Optional[bool] = Field(None, description="Whether the session has an active chat session")


class ChatSessionDebug(BaseModel):
    """Debug information about the chat session."""
    session_id: str = Field(..., description="ID of the chat session")
    has_active_memory: bool = Field(..., description="Whether the session has active memory")


class MessagesDebug(BaseModel):
    """Debug information about the messages in the session."""
    count: int = Field(..., description="Total number of messages")
    user_messages: int = Field(..., description="Number of messages from the user")
    assistant_messages: int = Field(..., description="Number of messages from the assistant")
    latest_message: Optional[str] = Field(None, description="Preview of the latest message")


class ToolChestDebug(BaseModel):
    """Debug information about the tool chest."""
    exists: bool = Field(..., description="Whether the tool chest exists")
    active_tools: Optional[List[str]] = Field(None, description="List of active tools")


class ChatLogDebug(BaseModel):
    """Debug information about the current chat log."""
    exists: bool = Field(..., description="Whether the current chat log exists")
    count: int = Field(..., description="Number of entries in the chat log")


class SessionDebugInfo(BaseModel):
    """Comprehensive debug information about a session."""
    session_id: str = Field(..., description="UI session ID")
    agent_c_session_id: str = Field(..., description="Agent C internal session ID")
    agent_name: str = Field(..., description="Name of the agent")
    created_at: str = Field(..., description="When the session was created")
    backend: str = Field(..., description="LLM backend being used")
    model_name: str = Field(..., description="Model name being used")
    session_manager: SessionManagerDebug = Field(..., description="Debug info about the session manager")
    chat_session: Optional[ChatSessionDebug] = Field(None, description="Debug info about the chat session")
    messages: Optional[MessagesDebug] = Field(None, description="Debug info about messages")
    recent_messages: Optional[List[MessagePreview]] = Field(None, description="Preview of recent messages")
    current_chat_Log: ChatLogDebug = Field(..., description="Debug info about the current chat log")
    tool_chest: ToolChestDebug = Field(..., description="Debug info about the tool chest")


class AgentBridgeParams(BaseModel):
    """Parameters for the Agent Bridge."""
    temperature: Optional[float] = Field(None, description="Temperature for response generation")
    reasoning_effort: Optional[str] = Field(None, description="Level of reasoning effort")
    extended_thinking: Optional[bool] = Field(None, description="Whether extended thinking is enabled")
    budget_tokens: Optional[int] = Field(None, description="Token budget for the agent")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for responses")


class InternalAgentParams(BaseModel):
    """Parameters for the internal agent."""
    type: str = Field(..., description="Type of the internal agent")
    temperature: Optional[float] = Field(None, description="Temperature for response generation")
    reasoning_effort: Optional[str] = Field(None, description="Level of reasoning effort")
    budget_tokens: Optional[int] = Field(None, description="Token budget for the agent")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for responses")


class AgentDebugInfo(BaseModel):
    """Debug information about an agent."""
    status: str = Field(..., description="Status of the agent debug operation")
    agent_bridge_params: AgentBridgeParams = Field(..., description="Parameters for the agent bridge")
    internal_agent_params: InternalAgentParams = Field(..., description="Parameters for the internal agent")