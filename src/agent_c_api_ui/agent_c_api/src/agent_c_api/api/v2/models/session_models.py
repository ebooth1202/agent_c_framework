# src/agent_c_api/api/v2/models/session_models.py
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from .response_models import APIStatus

# Session creation models
class SessionCreate(BaseModel):
    """Parameters for creating a new session"""
    model_config = ConfigDict(protected_namespaces=())
    model_id: str = Field(..., description="ID of the LLM model to use")
    persona_id: str = Field(default="default", description="ID of the persona to use")
    name: Optional[str] = Field(None, description="Optional session name")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
    temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")
    tools: Optional[List[str]] = Field(default_factory=list, description="List of tool IDs to enable")
    tool_ids: Optional[List[str]] = Field(None, description="Alternative format for tool IDs to enable")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

# Session information models
class SessionSummary(BaseModel):
    """Basic session information for listings"""
    model_config = ConfigDict(protected_namespaces=())
    id: UUID = Field(..., description="Session ID")
    model_id: str = Field(..., description="ID of the LLM model being used")
    persona_id: str = Field(..., description="ID of the persona being used")
    name: str = Field(..., description="Session name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last updated timestamp")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    is_active: bool = Field(..., description="Whether session is active")

class SessionDetail(SessionSummary):
    """Comprehensive session information"""
    agent_internal_id: Optional[str] = Field(None, description="Internal agent session ID")
    tools: List[str] = Field(default_factory=list, description="List of enabled tool IDs")
    tool_ids: List[str] = Field(..., description="Enabled tool IDs (alternative format)")
    temperature: Optional[float] = Field(None, description="Temperature parameter")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens parameter")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt being used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    message_count: Optional[int] = Field(None, description="Number of messages in the session")

# Session update models
class SessionUpdate(BaseModel):
    """Model for updating session properties"""
    name: Optional[str] = Field(None, description="Session name to update")
    persona_id: Optional[str] = Field(None, description="ID of the persona to use")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
    temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata to update")

# Session listing response
class SessionListResponse(BaseModel):
    """Paginated response for session listing"""
    items: List[SessionSummary] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total number of sessions")
    limit: int = Field(..., description="Maximum number of items per page")
    offset: int = Field(..., description="Current offset in the full result set")

# Agent-specific models
class AgentConfig(BaseModel):
    """Detailed agent configuration information"""
    model_id: str = Field(..., description="ID of the LLM model being used")
    persona_id: str = Field(..., description="ID of the persona being used")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
    temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")
    tools: List[str] = Field(default_factory=list, description="List of enabled tool IDs")

class AgentUpdate(BaseModel):
    """Model for updating agent configuration"""
    persona_id: Optional[str] = Field(None, description="ID of the persona to use")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Temperature parameter for the model")
    reasoning_effort: Optional[int] = Field(None, ge=0, le=10, description="Reasoning effort parameter (for OpenAI)")
    budget_tokens: Optional[int] = Field(None, ge=0, description="Budget tokens parameter (for Claude)")
    max_tokens: Optional[int] = Field(None, ge=0, description="Maximum tokens for model output")

class AgentUpdateResponse(BaseModel):
    """Response for agent configuration updates"""
    agent_config: AgentConfig = Field(..., description="Updated agent configuration")
    changes_applied: Dict[str, Any] = Field(default_factory=dict, description="Changes that were applied")
    changes_skipped: Dict[str, Any] = Field(default_factory=dict, description="Changes that were skipped")

# Response models
class SessionCreateResponse(BaseModel):
    """Response for session creation"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status")
    session_id: UUID = Field(..., description="Created session ID")
    name: str = Field(..., description="Session name")