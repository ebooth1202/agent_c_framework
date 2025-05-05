# src/agent_c_api/api/v2/models/file_models.py
from typing import Dict, Any, ClassVar
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class FileMeta(BaseModel):
    """Metadata about an uploaded file
    
    This model contains comprehensive metadata about a file that has been uploaded
    to a session. It includes basic information like filename and size, as well as
    processing metadata that indicates whether the file has been processed for
    text extraction or other analysis.
    """
    id: str = Field(
        ..., 
        description="Unique identifier for the file"
    )
    filename: str = Field(
        ..., 
        description="Original filename as provided during upload"
    )
    content_type: str = Field(
        ..., 
        description="MIME content type (e.g., 'application/pdf', 'image/jpeg')"
    )
    size: int = Field(
        ..., 
        description="File size in bytes"
    )
    uploaded_at: datetime = Field(
        ..., 
        description="Timestamp when the file was uploaded"
    )
    session_id: UUID = Field(
        ..., 
        description="UUID of the session this file belongs to"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata including processing status and results"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "file_abc123",
                    "filename": "document.pdf",
                    "content_type": "application/pdf",
                    "size": 1048576,
                    "uploaded_at": "2025-04-04T12:00:00Z",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "metadata": {
                        "processed": True,
                        "processing_status": "complete",
                        "page_count": 5
                    }
                },
                {
                    "id": "file_def456",
                    "filename": "screenshot.png",
                    "content_type": "image/png",
                    "size": 256000,
                    "uploaded_at": "2025-04-04T12:30:00Z",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "metadata": {
                        "processed": True,
                        "processing_status": "complete"
                    }
                }
            ]
        })


class FileUploadResponse(BaseModel):
    """Response after file upload
    
    This model represents the response returned when a file is successfully uploaded
    to a session. It contains the essential metadata needed to reference the file
    in subsequent requests, such as chat messages that include file attachments.
    """
    file_id: str = Field(
        ..., 
        description="Unique identifier for the uploaded file, used for referencing in chat messages"
    )
    filename: str = Field(
        ..., 
        description="Original filename as provided during upload"
    )
    content_type: str = Field(
        ..., 
        description="MIME content type detected for the file"
    )
    size: int = Field(
        ..., 
        description="File size in bytes"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "file_id": "file_abc123",
                    "filename": "report.pdf",
                    "content_type": "application/pdf",
                    "size": 2097152
                },
                {
                    "file_id": "file_def456",
                    "filename": "code_snippet.png",
                    "content_type": "image/png",
                    "size": 153600
                }
            ]
        })
