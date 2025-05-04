from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Request model for creating a new session"""
    model_id: str = Field(..., description="ID of the LLM model to use")
    persona_id: str = Field(default="default", description="ID of the persona to use")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
    temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")
    tools: Optional[List[str]] = Field(default_factory=list, description="List of tool IDs to enable")


class SessionSummary(BaseModel):
    """Summary information about a session"""
    id: str = Field(..., description="Session ID")
    model_id: str = Field(..., description="ID of the LLM model being used")
    persona_id: str = Field(..., description="ID of the persona being used")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class SessionDetail(BaseModel):
    """Detailed information about a session"""
    id: str = Field(..., description="Session ID")
    model_id: str = Field(..., description="ID of the LLM model being used")
    persona_id: str = Field(..., description="ID of the persona being used")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    agent_internal_id: str = Field(..., description="Internal agent session ID")
    tools: List[str] = Field(default_factory=list, description="List of enabled tool IDs")
    temperature: Optional[float] = Field(None, description="Temperature parameter")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens parameter")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt being used")


class SessionUpdate(BaseModel):
    """Model for updating session properties"""
    persona_id: Optional[str] = Field(None, description="ID of the persona to use")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
    temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
    reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
    budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")


class SessionListResponse(BaseModel):
    """Paginated response for session listing"""
    items: List[SessionSummary] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total number of sessions")
    limit: int = Field(..., description="Maximum number of items per page")
    offset: int = Field(..., description="Current offset in the full result set")


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