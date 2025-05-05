# src/agent_c_api/api/v2/models/debug_models.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MessagePreview(BaseModel):
    """
    Preview of a chat message in the session.
    
    Contains a truncated view of message content and metadata for debugging purposes.
    """
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content_preview: str = Field(..., description="Preview of the message content (truncated)")
    timestamp: Optional[str] = Field(None, description="Timestamp when the message was sent")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content_preview": "Can you help me debug my Python code...",
                    "timestamp": "2025-05-04T14:22:15Z"
                },
                {
                    "role": "assistant",
                    "content_preview": "I'd be happy to help with your Python code...",
                    "timestamp": "2025-05-04T14:22:45Z"
                }
            ]
        }
    }


class SessionManagerDebug(BaseModel):
    """
    Debug information about the session manager.
    
    Provides status information about the session manager component that coordinates
    the session's resources and lifecycle.
    """
    exists: bool = Field(..., description="Whether the session manager exists")
    user_id: Optional[str] = Field(None, description="User ID associated with the session")
    has_chat_session: Optional[bool] = Field(None, description="Whether the session has an active chat session")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "exists": True,
                    "user_id": "user-12345",
                    "has_chat_session": True
                },
                {
                    "exists": True,
                    "user_id": "user-67890",
                    "has_chat_session": False
                }
            ]
        }
    }


class ChatSessionDebug(BaseModel):
    """
    Debug information about the chat session.
    
    Contains status information about the active chat session, including memory state.
    """
    session_id: str = Field(..., description="ID of the chat session")
    has_active_memory: bool = Field(..., description="Whether the session has active memory")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "chat-sess-abc123",
                    "has_active_memory": True
                }
            ]
        }
    }


class MessagesDebug(BaseModel):
    """
    Debug information about the messages in the session.
    
    Provides aggregate statistics about messages exchanged in the session,
    including counts by role and a preview of the most recent message.
    """
    count: int = Field(..., description="Total number of messages")
    user_messages: int = Field(..., description="Number of messages from the user")
    assistant_messages: int = Field(..., description="Number of messages from the assistant")
    latest_message: Optional[str] = Field(None, description="Preview of the latest message")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "count": 7,
                    "user_messages": 3,
                    "assistant_messages": 4,
                    "latest_message": "I'll analyze that code snippet now..."
                }
            ]
        }
    }


class ToolChestDebug(BaseModel):
    """
    Debug information about the tool chest.
    
    Contains status information about the tool chest component that manages
    the available tools for the agent in this session.
    """
    exists: bool = Field(..., description="Whether the tool chest exists")
    active_tools: Optional[List[str]] = Field(None, description="List of active tools")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "exists": True,
                    "active_tools": ["web_search", "code_interpreter", "file_browser"]
                },
                {
                    "exists": True,
                    "active_tools": []
                }
            ]
        }
    }


class ChatLogDebug(BaseModel):
    """
    Debug information about the current chat log.
    
    Provides status information about the chat log component that stores
    detailed information about the conversation history.
    """
    exists: bool = Field(..., description="Whether the current chat log exists")
    count: int = Field(..., description="Number of entries in the chat log")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "exists": True,
                    "count": 12
                },
                {
                    "exists": False,
                    "count": 0
                }
            ]
        }
    }


class SessionDebugInfo(BaseModel):
    """
    Comprehensive debug information about a session.
    
    Provides detailed diagnostic information about all components of an Agent C session,
    including identifiers, configuration, message statistics, and component status.
    This information is primarily intended for development, troubleshooting, and
    administrative purposes.
    """
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
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "ui-sess-def456",
                    "agent_c_session_id": "internal-sess-xyz789",
                    "agent_name": "Tech Support Agent",
                    "created_at": "2025-05-04T13:45:22Z",
                    "backend": "openai",
                    "model_name": "gpt-4",
                    "session_manager": {
                        "exists": True,
                        "user_id": "user-12345",
                        "has_chat_session": True
                    },
                    "chat_session": {
                        "session_id": "chat-sess-abc123",
                        "has_active_memory": True
                    },
                    "messages": {
                        "count": 7,
                        "user_messages": 3,
                        "assistant_messages": 4,
                        "latest_message": "I'll analyze that code snippet now..."
                    },
                    "recent_messages": [
                        {
                            "role": "user",
                            "content_preview": "Can you help me debug my Python code...",
                            "timestamp": "2025-05-04T14:22:15Z"
                        },
                        {
                            "role": "assistant",
                            "content_preview": "I'd be happy to help with your Python code...",
                            "timestamp": "2025-05-04T14:22:45Z"
                        }
                    ],
                    "current_chat_Log": {
                        "exists": True,
                        "count": 12
                    },
                    "tool_chest": {
                        "exists": True,
                        "active_tools": ["web_search", "code_interpreter", "file_browser"]
                    }
                }
            ]
        }
    }


class AgentBridgeParams(BaseModel):
    """
    Parameters for the Agent Bridge.
    
    Contains configuration parameters for the bridge component that connects
    the API with the underlying agent implementation.
    """
    temperature: Optional[float] = Field(None, description="Temperature for response generation (0.0-1.0)")
    reasoning_effort: Optional[str] = Field(None, description="Level of reasoning effort (minimal, moderate, thorough)")
    extended_thinking: Optional[bool] = Field(None, description="Whether extended thinking is enabled")
    budget_tokens: Optional[int] = Field(None, description="Token budget for the agent")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for responses")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "temperature": 0.7,
                    "reasoning_effort": "thorough",
                    "extended_thinking": True,
                    "budget_tokens": 8000,
                    "max_tokens": 4000
                }
            ]
        }
    }


class InternalAgentParams(BaseModel):
    """
    Parameters for the internal agent.
    
    Contains configuration parameters for the underlying agent implementation
    that generates responses and performs reasoning.
    """
    type: str = Field(..., description="Type of the internal agent (e.g., 'ReactJSAgent', 'AssistantAgent')")
    temperature: Optional[float] = Field(None, description="Temperature for response generation (0.0-1.0)")
    reasoning_effort: Optional[str] = Field(None, description="Level of reasoning effort (minimal, moderate, thorough)")
    budget_tokens: Optional[int] = Field(None, description="Token budget for the agent")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for responses")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "ReactJSAgent",
                    "temperature": 0.5,
                    "reasoning_effort": "thorough",
                    "budget_tokens": 8000,
                    "max_tokens": 4000
                }
            ]
        }
    }


class AgentDebugInfo(BaseModel):
    """
    Debug information about an agent.
    
    Provides detailed diagnostic information about an agent's configuration,
    including both the bridge parameters and internal agent parameters.
    This information is primarily intended for development, troubleshooting,
    and monitoring agent behavior.
    """
    status: str = Field(..., description="Status of the agent debug operation ('success' or error message)")
    agent_bridge_params: AgentBridgeParams = Field(..., description="Parameters for the agent bridge")
    internal_agent_params: InternalAgentParams = Field(..., description="Parameters for the internal agent")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "agent_bridge_params": {
                        "temperature": 0.7,
                        "reasoning_effort": "thorough",
                        "extended_thinking": True,
                        "budget_tokens": 8000,
                        "max_tokens": 4000
                    },
                    "internal_agent_params": {
                        "type": "ReactJSAgent",
                        "temperature": 0.5,
                        "reasoning_effort": "thorough",
                        "budget_tokens": 8000,
                        "max_tokens": 4000
                    }
                }
            ]
        }
    }