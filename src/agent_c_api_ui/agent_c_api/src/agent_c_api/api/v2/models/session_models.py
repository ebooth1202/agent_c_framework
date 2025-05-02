# src/agent_c_api/api/v2/models/session_models.py
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from .response_models import APIStatus

class SessionCreate(BaseModel):
    """Parameters for creating a new session"""
    name: Optional[str] = Field(None, description="Optional session name")
    model_id: Optional[str] = Field(None, description="LLM model ID to use")
    persona_id: Optional[str] = Field(None, description="Persona ID to use")
    tool_ids: Optional[List[str]] = Field(None, description="Tool IDs to enable")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class SessionSummary(BaseModel):
    """Basic session information for listings"""
    id: UUID = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    model_id: str = Field(..., description="LLM model ID")
    persona_id: str = Field(..., description="Persona ID")
    is_active: bool = Field(..., description="Whether session is active")

class SessionDetail(SessionSummary):
    """Comprehensive session information"""
    tool_ids: List[str] = Field(..., description="Enabled tool IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    message_count: int = Field(..., description="Number of messages in the session")

class SessionUpdate(BaseModel):
    """Parameters for updating a session"""
    name: Optional[str] = Field(None, description="Session name to update")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata to update")

# Response models
class SessionCreateResponse(BaseModel):
    """Response for session creation"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status")
    session_id: UUID = Field(..., description="Created session ID")
    name: str = Field(..., description="Session name")