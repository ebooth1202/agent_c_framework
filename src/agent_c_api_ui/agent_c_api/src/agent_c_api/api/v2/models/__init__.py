# src/agent_c_api/api/v2/models/__init__.py
"""
API v2 models package.

This package contains all the Pydantic models used in the v2 API.
Model organization:
- session_models.py: Contains core session and agent configuration models
- agent_models.py: Contains models specific to agent capabilities and info
- chat_models.py: Contains message and chat-related models
- tool_models.py: Contains tool-related models
- file_models.py: Contains file and document-related models
- history_models.py: Contains models for interaction history
- response_models.py: Contains common response structure models
- debug_models.py: Contains debug and diagnostic models

IMPORTANT: When using agent configuration models (AgentConfig, AgentUpdate):
  - Always import from session_models.py, not agent_models.py
  - agent_models.py re-exports these from session_models.py to maintain compatibility
"""

# Response models
from .response_models import (
    APIStatus,
    APIResponse,
    PaginationMeta,
    PaginatedResponse
)

# Session models
from .session_models import (
    SessionCreate,
    SessionSummary,
    SessionDetail,
    SessionUpdate,
    SessionListResponse,
    AgentConfig,
    AgentUpdate,
    AgentUpdateResponse,
    SessionCreateResponse
)

# Agent models
from .agent_models import (
    ModelParameter,
    ModelInfo,
    PersonaInfo
)

# Chat models
from .chat_models import (
    FileBlock,
    ChatMessageContent,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatEventType
)

# File models
from .file_models import (
    FileMeta,
    FileUploadResponse
)

# History models
from .history_models import (
    HistorySummary,
    HistoryDetail,
    PaginationParams,
    HistoryListResponse,
    EventFilter,
    StoredEvent,
    ReplayStatus,
    ReplayControl
)

# Tool models
from .tool_models import (
    ToolParameter,
    ToolInfo,
    ToolCategory,
    ToolsList,
    SessionTools,
    ToolsUpdate,
    ToolCall,
    ToolResult
)

# Debug models
from .debug_models import (
    MessagePreview,
    SessionManagerDebug,
    ChatSessionDebug,
    MessagesDebug,
    ToolChestDebug,
    ChatLogDebug,
    SessionDebugInfo,
    AgentBridgeParams,
    InternalAgentParams,
    AgentDebugInfo
)

# Groupings for convenient access
response_models = [APIStatus, APIResponse, PaginationMeta, PaginatedResponse]

session_models = [
    SessionCreate, SessionSummary, SessionDetail, SessionUpdate,
    SessionListResponse, SessionCreateResponse
]

agent_models = [AgentConfig, AgentUpdate, AgentUpdateResponse, ModelParameter, ModelInfo, PersonaInfo]

chat_models = [
    FileBlock, ChatMessageContent, ChatMessage, ChatRequest, ChatResponse, ChatEventType
]

file_models = [FileMeta, FileUploadResponse]

history_models = [
    HistorySummary, HistoryDetail, PaginationParams, HistoryListResponse,
    EventFilter, StoredEvent, ReplayStatus, ReplayControl
]

tool_models = [
    ToolParameter, ToolInfo, ToolCategory, ToolsList,
    SessionTools, ToolsUpdate, ToolCall, ToolResult
]

debug_models = [
    MessagePreview, SessionManagerDebug, ChatSessionDebug, MessagesDebug,
    ToolChestDebug, ChatLogDebug, SessionDebugInfo, AgentBridgeParams,
    InternalAgentParams, AgentDebugInfo
]