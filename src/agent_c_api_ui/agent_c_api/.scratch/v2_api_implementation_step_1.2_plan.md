# Agent C API V2 - Second Implementation Step

## Overview

This document outlines the specific changes we'll make for the second implementation step of the v2 API, focusing on implementing core Pydantic models. This builds upon our established project structure and prepares for endpoint implementation.

## Model Implementation Changes

### 1. Create Session Models

**File**: `/api/v2/models/session_models.py`

```python
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
```

### 2. Create Agent Models

**File**: `/api/v2/models/agent_models.py`

```python
# src/agent_c_api/api/v2/models/agent_models.py
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class ModelParameter(BaseModel):
    """LLM model parameter"""
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    description: Optional[str] = Field(None, description="Parameter description")
    type: str = Field(..., description="Parameter type (string, int, float, boolean)")

class AgentConfig(BaseModel):
    """Current agent configuration in a session"""
    model_id: str = Field(..., description="LLM model ID")
    persona_id: str = Field(..., description="Persona ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    system_message: Optional[str] = Field(None, description="Custom system message")

class AgentUpdate(BaseModel):
    """Parameters for updating agent settings"""
    model_id: Optional[str] = Field(None, description="LLM model ID to use")
    persona_id: Optional[str] = Field(None, description="Persona ID to use")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Model parameters to update")
    system_message: Optional[str] = Field(None, description="Custom system message")

class ModelInfo(BaseModel):
    """Information about an LLM model"""
    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    provider: str = Field(..., description="Model provider (OpenAI, Anthropic, etc.)")
    capabilities: List[str] = Field(default_factory=list, description="Model capabilities")
    parameters: List[ModelParameter] = Field(default_factory=list, description="Available parameters")

class PersonaInfo(BaseModel):
    """Information about a persona"""
    id: str = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    capabilities: List[str] = Field(default_factory=list, description="Persona capabilities")
    system_message: Optional[str] = Field(None, description="System message template")
```

### 3. Create Tool Models

**File**: `/api/v2/models/tool_models.py`

```python
# src/agent_c_api/api/v2/models/tool_models.py
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if any")

class ToolInfo(BaseModel):
    """Information about a tool"""
    id: str = Field(..., description="Tool ID")
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: str = Field(..., description="Tool category")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Tool parameters")
    examples: List[str] = Field(default_factory=list, description="Usage examples")

class ToolCategory(BaseModel):
    """A category of tools"""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    tools: List[ToolInfo] = Field(..., description="Tools in this category")

class ToolsList(BaseModel):
    """Comprehensive list of available tools"""
    categories: List[ToolCategory] = Field(..., description="Tool categories")
    
class SessionTools(BaseModel):
    """Tools currently enabled in a session"""
    enabled_tools: List[str] = Field(..., description="Enabled tool IDs")
    available_tools: List[str] = Field(..., description="Available but not enabled tool IDs")

class ToolsUpdate(BaseModel):
    """Parameters for updating session tools"""
    enabled_tools: List[str] = Field(..., description="Tool IDs to enable")
    
class ToolCall(BaseModel):
    """A call to a tool"""
    tool_id: str = Field(..., description="Tool ID")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    
class ToolResult(BaseModel):
    """Result of a tool call"""
    tool_id: str = Field(..., description="Tool ID")
    success: bool = Field(..., description="Whether call was successful")
    result: Any = Field(..., description="Result value")
    error: Optional[str] = Field(None, description="Error message if failed")
```

### 4. Create Chat Models

**File**: `/api/v2/models/chat_models.py`

```python
# src/agent_c_api/api/v2/models/chat_models.py
from typing import Dict, List, Optional, Any, Union, Literal
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
    
    @field_validator('text')
    @classmethod
    def text_required_for_text_type(cls, v: Optional[str], info) -> Optional[str]:
        if info.data.get('type') == 'text' and v is None:
            raise ValueError('text is required when type is text')
        return v
        
    @field_validator('file_id')
    @classmethod
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
```

### 5. Create File Models

**File**: `/api/v2/models/file_models.py`

```python
# src/agent_c_api/api/v2/models/file_models.py
from typing import Dict, List, Optional, Any
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
```

### 6. Create History Models

**File**: `/api/v2/models/history_models.py`

```python
# src/agent_c_api/api/v2/models/history_models.py
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from .chat_models import ChatMessage

class HistorySummary(BaseModel):
    """Summary of a recorded session history"""
    session_id: UUID = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    message_count: int = Field(..., description="Number of messages")
    duration: int = Field(..., description="Session duration in seconds")

class EventFilter(BaseModel):
    """Parameters for filtering history events"""
    event_types: Optional[List[str]] = Field(None, description="Event types to include")
    start_time: Optional[datetime] = Field(None, description="Start time for events")
    end_time: Optional[datetime] = Field(None, description="End time for events")
    limit: int = Field(100, description="Maximum number of events to return")

class Event(BaseModel):
    """A recorded event in session history"""
    id: str = Field(..., description="Event ID")
    session_id: UUID = Field(..., description="Session ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")

class ReplayStatus(BaseModel):
    """Status of a session replay"""
    session_id: UUID = Field(..., description="Session ID")
    is_playing: bool = Field(..., description="Whether replay is playing")
    current_position: datetime = Field(..., description="Current replay position")
    start_time: datetime = Field(..., description="Session start time")
    end_time: datetime = Field(..., description="Session end time")

class ReplayControl(BaseModel):
    """Parameters for controlling replay"""
    action: Literal["play", "pause", "seek"] = Field(..., description="Control action")
    position: Optional[datetime] = Field(None, description="Position to seek to (for seek action)")
    speed: Optional[float] = Field(None, description="Playback speed multiplier (for play action)")
```

### 7. Create Response Models

**File**: `/api/v2/models/response_models.py`

```python
# src/agent_c_api/api/v2/models/response_models.py
from typing import Dict, List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIStatus(BaseModel):
    """Standard API response status"""
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Status message")
    error_code: Optional[str] = Field(None, description="Error code if unsuccessful")

class APIResponse(Generic[T], BaseModel):
    """Standard API response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status")
    data: Optional[T] = Field(None, description="Response data")

class PaginationMeta(BaseModel):
    """Metadata for paginated responses"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

class PaginatedResponse(Generic[T], BaseModel):
    """Paginated API response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status")
    data: List[T] = Field(default_factory=list, description="Page of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
```

### 8. Create Model Tests

Create tests for the new models to ensure they validate correctly.

**File**: `src/agent_c_api/tests/v2/models/test_session_models.py`

```python
# src/agent_c_api/tests/v2/models/test_session_models.py
import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from agent_c_api.api.v2.models.session_models import (
    SessionCreate, SessionSummary, SessionDetail, SessionUpdate
)

def test_session_create_model():
    # Test with minimal fields
    session = SessionCreate()
    assert session.name is None
    assert session.model_id is None
    assert session.persona_id is None
    assert session.tool_ids is None
    assert session.metadata is None
    
    # Test with all fields
    session = SessionCreate(
        name="Test Session",
        model_id="gpt-4",
        persona_id="default",
        tool_ids=["calculator", "weather"],
        metadata={"created_by": "test"}
    )
    assert session.name == "Test Session"
    assert session.model_id == "gpt-4"
    assert session.persona_id == "default"
    assert session.tool_ids == ["calculator", "weather"]
    assert session.metadata == {"created_by": "test"}

def test_session_summary_model():
    now = datetime.now()
    session_id = uuid4()
    
    # Test creating a valid summary
    summary = SessionSummary(
        id=session_id,
        name="Test Session",
        created_at=now,
        updated_at=now,
        model_id="gpt-4",
        persona_id="default",
        is_active=True
    )
    
    assert summary.id == session_id
    assert summary.name == "Test Session"
    assert summary.created_at == now
    assert summary.updated_at == now
    assert summary.model_id == "gpt-4"
    assert summary.persona_id == "default"
    assert summary.is_active is True

def test_session_detail_model():
    now = datetime.now()
    session_id = uuid4()
    
    # Test creating a valid detail object
    detail = SessionDetail(
        id=session_id,
        name="Test Session",
        created_at=now,
        updated_at=now,
        model_id="gpt-4",
        persona_id="default",
        is_active=True,
        tool_ids=["calculator", "weather"],
        metadata={"created_by": "test"},
        message_count=5
    )
    
    assert detail.id == session_id
    assert detail.name == "Test Session"
    assert detail.tool_ids == ["calculator", "weather"]
    assert detail.metadata == {"created_by": "test"}
    assert detail.message_count == 5

def test_session_update_model():
    # Test with no fields (valid but does nothing)
    update = SessionUpdate()
    assert update.name is None
    assert update.metadata is None
    
    # Test with all fields
    update = SessionUpdate(
        name="Updated Name",
        metadata={"updated": True}
    )
    assert update.name == "Updated Name"
    assert update.metadata == {"updated": True}
```

**File**: `src/agent_c_api/tests/v2/models/test_response_models.py`

```python
# src/agent_c_api/tests/v2/models/test_response_models.py
import pytest
from typing import List
from pydantic import BaseModel
from agent_c_api.api.v2.models.response_models import (
    APIStatus, APIResponse, PaginationMeta, PaginatedResponse
)

def test_api_status_model():
    # Test default values
    status = APIStatus()
    assert status.success is True
    assert status.message is None
    assert status.error_code is None
    
    # Test with custom values
    status = APIStatus(success=False, message="An error occurred", error_code="VALIDATION_ERROR")
    assert status.success is False
    assert status.message == "An error occurred"
    assert status.error_code == "VALIDATION_ERROR"

def test_api_response_model():
    # Simple data model for testing
    class TestData(BaseModel):
        name: str
        value: int
    
    # Test with default status
    response = APIResponse[TestData](data=TestData(name="test", value=42))
    assert response.status.success is True
    assert response.data.name == "test"
    assert response.data.value == 42
    
    # Test with custom status
    status = APIStatus(success=False, message="Error", error_code="TEST_ERROR")
    response = APIResponse[TestData](status=status, data=None)
    assert response.status.success is False
    assert response.status.message == "Error"
    assert response.data is None

def test_pagination_meta_model():
    # Test valid pagination metadata
    meta = PaginationMeta(page=2, page_size=10, total_items=25, total_pages=3)
    assert meta.page == 2
    assert meta.page_size == 10
    assert meta.total_items == 25
    assert meta.total_pages == 3

def test_paginated_response_model():
    # Test with list of strings
    pagination = PaginationMeta(page=1, page_size=2, total_items=3, total_pages=2)
    response = PaginatedResponse[str](
        data=["item1", "item2"],
        pagination=pagination
    )
    
    assert response.status.success is True
    assert response.data == ["item1", "item2"]
    assert response.pagination.page == 1
    assert response.pagination.total_items == 3
```

## Testing Plan

In addition to the model tests above, we will create and run the following tests:

1. Verify model validations work correctly for edge cases
2. Test model conversions from v1 formats to v2 formats
3. Ensure serialization and deserialization works correctly

## Justification

This second implementation step creates the core data models that will be used throughout the v2 API. These Pydantic models provide:

1. **Type Safety**: Strong typing and validation for all API data
2. **Documentation**: Self-documenting through types and descriptions
3. **Consistency**: Standard patterns across all resources
4. **Validation**: Automatic request and response validation

By implementing these models first, we establish the contract for our API before writing any endpoint logic. This ensures that all endpoints will have consistent data structures and validation.

The models are designed to be:
- **Complete**: Covering all data needed for the API
- **Flexible**: Supporting various use cases
- **Validated**: With appropriate validators and type checks
- **Documented**: With clear field descriptions

## Next Steps After Approval

Once these core models are approved and implemented, we'll move to planning the implementation session for the common utilities and the first set of endpoints (configuration resources) as outlined in our implementation plan.