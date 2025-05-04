# src/agent_c_api/api/v2/models/file_models.py
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class FileMeta(BaseModel):
    """Metadata about an uploaded file"""
    id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    session_id: UUID = Field(..., description="Session ID the file belongs to")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    size: int = Field(..., description="File size in bytes")