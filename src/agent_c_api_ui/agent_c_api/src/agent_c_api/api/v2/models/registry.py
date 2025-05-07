"""
Model Registry - Single source of truth for all API v2 models.

This module provides a registry of all models used in the v2 API,
which can be used for documentation, validation, and testing.

Key features:
- Complete inventory of all models in the v2 API
- Organization by domain/category
- Methods to retrieve models by name or domain
- Validation to prevent model duplication

This registry should be kept up-to-date whenever models are added,
removed, or modified.
"""

from typing import Dict, List, Type, Set, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel

# Import all models
from .response_models import (
    APIStatus,
    APIResponse,
    PaginationMeta,
    PaginatedResponse
)

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

from .agent_models import (
    ModelParameter,
    ModelInfo,
    PersonaInfo
)

from .chat_models import (
    FileBlock,
    ChatMessageContent,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatEventType
)

from .file_models import (
    FileMeta,
    FileUploadResponse
)

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

# Registry structure - Pydantic models only
MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {
    # Response models
    "APIStatus": APIStatus,
    "APIResponse": APIResponse,
    "PaginationMeta": PaginationMeta,
    "PaginatedResponse": PaginatedResponse,
    
    # Session models
    "SessionCreate": SessionCreate,
    "SessionSummary": SessionSummary,
    "SessionDetail": SessionDetail,
    "SessionUpdate": SessionUpdate,
    "SessionListResponse": SessionListResponse,
    "SessionCreateResponse": SessionCreateResponse,
    "AgentConfig": AgentConfig,
    "AgentUpdate": AgentUpdate,
    "AgentUpdateResponse": AgentUpdateResponse,
    
    # Agent models
    "ModelParameter": ModelParameter,
    "ModelInfo": ModelInfo,
    "PersonaInfo": PersonaInfo,
    
    # Chat models
    "FileBlock": FileBlock,
    "ChatMessageContent": ChatMessageContent,
    "ChatMessage": ChatMessage,
    "ChatRequest": ChatRequest,
    "ChatResponse": ChatResponse,
    
    # File models
    "FileMeta": FileMeta,
    "FileUploadResponse": FileUploadResponse,
    
    # History models
    "HistorySummary": HistorySummary,
    "HistoryDetail": HistoryDetail,
    "PaginationParams": PaginationParams,
    "HistoryListResponse": HistoryListResponse,
    "EventFilter": EventFilter,
    "StoredEvent": StoredEvent,
    "ReplayStatus": ReplayStatus,
    "ReplayControl": ReplayControl,
    
    # Tool models
    "ToolParameter": ToolParameter,
    "ToolInfo": ToolInfo,
    "ToolCategory": ToolCategory,
    "ToolsList": ToolsList,
    "SessionTools": SessionTools,
    "ToolsUpdate": ToolsUpdate,
    "ToolCall": ToolCall,
    "ToolResult": ToolResult,
    
    # Debug models
    "MessagePreview": MessagePreview,
    "SessionManagerDebug": SessionManagerDebug,
    "ChatSessionDebug": ChatSessionDebug,
    "MessagesDebug": MessagesDebug,
    "ToolChestDebug": ToolChestDebug,
    "ChatLogDebug": ChatLogDebug,
    "SessionDebugInfo": SessionDebugInfo,
    "AgentBridgeParams": AgentBridgeParams,
    "InternalAgentParams": InternalAgentParams,
    "AgentDebugInfo": AgentDebugInfo,
}

# Registry for enums and other non-model types
ENUM_REGISTRY: Dict[str, Type[Enum]] = {
    "ChatEventType": ChatEventType,
}

# Organization by domain
RESPONSE_MODELS: List[Type[BaseModel]] = [
    APIStatus, APIResponse, PaginationMeta, PaginatedResponse
]

SESSION_MODELS: List[Type[BaseModel]] = [
    SessionCreate, SessionSummary, SessionDetail, SessionUpdate,
    SessionListResponse, SessionCreateResponse
]

AGENT_MODELS: List[Type[BaseModel]] = [
    AgentConfig, AgentUpdate, AgentUpdateResponse,
    ModelParameter, ModelInfo, PersonaInfo
]

CHAT_MODELS: List[Type[Union[BaseModel, Enum]]] = [
    FileBlock, ChatMessageContent, ChatMessage,
    ChatRequest, ChatResponse, ChatEventType
]

FILE_MODELS: List[Type[BaseModel]] = [
    FileMeta, FileUploadResponse
]

HISTORY_MODELS: List[Type[BaseModel]] = [
    HistorySummary, HistoryDetail, PaginationParams, HistoryListResponse,
    EventFilter, StoredEvent, ReplayStatus, ReplayControl
]

TOOL_MODELS: List[Type[BaseModel]] = [
    ToolParameter, ToolInfo, ToolCategory, ToolsList,
    SessionTools, ToolsUpdate, ToolCall, ToolResult
]

DEBUG_MODELS: List[Type[BaseModel]] = [
    MessagePreview, SessionManagerDebug, ChatSessionDebug, MessagesDebug,
    ToolChestDebug, ChatLogDebug, SessionDebugInfo, AgentBridgeParams,
    InternalAgentParams, AgentDebugInfo
]

# Domain mapping
DOMAIN_MODELS: Dict[str, List[Type[BaseModel]]] = {
    "response": RESPONSE_MODELS,
    "session": SESSION_MODELS,
    "agent": AGENT_MODELS,
    "chat": CHAT_MODELS,
    "file": FILE_MODELS,
    "history": HISTORY_MODELS,
    "tool": TOOL_MODELS,
    "debug": DEBUG_MODELS
}

# Helper functions
def get_model_by_name(name: str) -> Optional[Type[BaseModel]]:
    """Get a model class by its name.
    
    Args:
        name: The name of the model class
        
    Returns:
        The model class if found, None otherwise
    """
    return MODEL_REGISTRY.get(name)

def get_enum_by_name(name: str) -> Optional[Type[Enum]]:
    """Get an enum class by its name.
    
    Args:
        name: The name of the enum class
        
    Returns:
        The enum class if found, None otherwise
    """
    return ENUM_REGISTRY.get(name)

def get_type_by_name(name: str) -> Optional[Type[Any]]:
    """Get any registered type by its name.
    
    Args:
        name: The name of the type
        
    Returns:
        The type if found, None otherwise
    """
    return MODEL_REGISTRY.get(name) or ENUM_REGISTRY.get(name)

def list_models_by_domain(domain: str) -> List[Type[Union[BaseModel, Enum]]]:
    """List all models in a specific domain.
    
    Args:
        domain: The domain name (e.g., "session", "agent")
        
    Returns:
        List of model and enum classes in the specified domain
    """
    return DOMAIN_MODELS.get(domain, [])

def get_all_model_names() -> List[str]:
    """Get a list of all model names.
    
    Returns:
        List of all model names in the registry
    """
    return list(MODEL_REGISTRY.keys())

def get_all_enum_names() -> List[str]:
    """Get a list of all enum names.
    
    Returns:
        List of all enum names in the registry
    """
    return list(ENUM_REGISTRY.keys())

def get_all_type_names() -> List[str]:
    """Get a list of all registered type names.
    
    Returns:
        List of all type names in the registries
    """
    return list(MODEL_REGISTRY.keys()) + list(ENUM_REGISTRY.keys())

def verify_no_duplicate_models() -> bool:
    """Verify that there are no duplicate model classes in the registry.
    
    Returns:
        True if no duplicates are found, False otherwise
    """
    model_classes = list(MODEL_REGISTRY.values())
    return len(model_classes) == len(set(model_classes))

def get_duplicate_model_names() -> List[str]:
    """Get a list of model names that have duplicate classes.
    
    Returns:
        List of model names with duplicate classes
    """
    seen_classes: Set[Type[BaseModel]] = set()
    duplicates: List[str] = []
    
    for name, model_class in MODEL_REGISTRY.items():
        if model_class in seen_classes:
            duplicates.append(name)
        else:
            seen_classes.add(model_class)
    
    return duplicates