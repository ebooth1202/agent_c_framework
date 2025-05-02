# Agent C API V2 - Implementation Step 3.1: Session CRUD Operations

## Overview

This document outlines the implementation plan for Phase 3, Step 1 of our API v2 development, focusing on Session CRUD (Create, Read, Update, Delete) operations. These endpoints will provide the foundation for managing user sessions within the API, allowing clients to create, retrieve, list, update, and delete sessions.

## 1. Current State Assessment

Based on analysis of the v1 API and our redesign findings, the current session management functionality is implemented in:

- `/v1/sessions.py` - Contains endpoints for session initialization and verification
- `/core/agent_manager.py` - Contains the `UItoAgentBridgeManager` class that manages sessions

The v1 API has some limitations:
- Inconsistent naming (`initialize_agent` endpoint creates a session)
- Missing endpoint for deleting a single session
- Mix of RESTful and RPC patterns

## 2. Implementation Components

### 2.1 Model Definitions

We'll create the following Pydantic models in `/api/v2/sessions/models.py`:

1. **SessionCreate** - Request model for session creation:
   ```python
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
   ```

2. **SessionSummary** - Basic session information for list response:
   ```python
   class SessionSummary(BaseModel):
       """Summary information about a session"""
       id: str = Field(..., description="Session ID")
       model_id: str = Field(..., description="ID of the LLM model being used")
       persona_id: str = Field(..., description="ID of the persona being used")
       created_at: datetime = Field(..., description="Session creation timestamp")
       last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
   ```

3. **SessionDetail** - Detailed session information:
   ```python
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
   ```

4. **SessionUpdate** - Model for update operations:
   ```python
   class SessionUpdate(BaseModel):
       """Model for updating session properties"""
       persona_id: Optional[str] = Field(None, description="ID of the persona to use")
       custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
       temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
       reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
       budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
       max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")
   ```

5. **SessionListResponse** - Paginated response for listing sessions:
   ```python
   class SessionListResponse(BaseModel):
       """Paginated response for session listing"""
       items: List[SessionSummary] = Field(..., description="List of sessions")
       total: int = Field(..., description="Total number of sessions")
       limit: int = Field(..., description="Maximum number of items per page")
       offset: int = Field(..., description="Current offset in the full result set")
   ```

### 2.2 Service Implementation

We'll create a `SessionService` class in `/api/v2/sessions/services.py`:

```python
class SessionService:
    """Service for managing sessions"""
    
    def __init__(self, agent_manager: UItoAgentBridgeManager = Depends(get_agent_manager)):
        self.agent_manager = agent_manager
    
    async def create_session(self, session_data: SessionCreate) -> SessionDetail:
        """Create a new session"""
        # Convert SessionCreate to AgentInitializationParams
        # Call agent_manager to create session
        # Return SessionDetail with the created session
    
    async def get_sessions(self, limit: int = 10, offset: int = 0) -> SessionListResponse:
        """Get list of sessions with pagination"""
        # Get sessions from agent_manager
        # Apply pagination
        # Return SessionListResponse
    
    async def get_session(self, session_id: str) -> Optional[SessionDetail]:
        """Get detailed information about a specific session"""
        # Get session from agent_manager
        # Convert to SessionDetail
        # Return SessionDetail
    
    async def update_session(self, session_id: str, update_data: SessionUpdate) -> SessionDetail:
        """Update session properties"""
        # Convert SessionUpdate to AgentUpdateParams
        # Call agent_manager to update session
        # Return updated SessionDetail
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        # Call agent_manager to delete session
        # Return success status
```

### 2.3 Router Implementation

We'll create a router in `/api/v2/sessions/router.py`:

```python
router = APIRouter(tags=["sessions"], prefix="/sessions")

@router.post("", response_model=SessionDetail, status_code=201)
@version(2)
async def create_session(
    session_data: SessionCreate,
    service: SessionService = Depends(get_session_service)
):
    """
    Create a new agent session.
    
    Creates a new session with the specified model, persona, and configuration.
    Returns the session details including the session ID.
    """
    return await service.create_session(session_data)

@router.get("", response_model=SessionListResponse)
@version(2)
async def list_sessions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: SessionService = Depends(get_session_service)
):
    """
    List all sessions.
    
    Retrieves a paginated list of all active sessions.
    """
    return await service.get_sessions(limit, offset)

@router.get("/{session_id}", response_model=SessionDetail)
@version(2)
async def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Get session details.
    
    Retrieves detailed information about a specific session.
    """
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session

@router.patch("/{session_id}", response_model=SessionDetail)
@version(2)
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    service: SessionService = Depends(get_session_service)
):
    """
    Update session properties.
    
    Updates one or more properties of a session, such as persona or model parameters.
    """
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return await service.update_session(session_id, update_data)

@router.delete("/{session_id}", status_code=204)
@version(2)
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Delete a session.
    
    Permanently removes a session and releases its resources.
    """
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    success = await service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")
```

## 3. Test Plan

### 3.1 Unit Tests

We'll create thorough unit tests in `/tests/v2/sessions/test_sessions.py`:

1. **Service Tests**
   - Test session creation with various parameters
   - Test session retrieval
   - Test session listing with pagination
   - Test session updates
   - Test session deletion
   - Test error handling (e.g., non-existent sessions)

2. **Endpoint Tests**
   - Test all endpoints with mocked service responses
   - Test validation errors (e.g., invalid session IDs, invalid model parameters)
   - Test error responses (404, 500)
   - Test successful responses (200, 201, 204)

### 3.2 Integration Tests

We'll create integration tests that verify the entire flow from API to agent manager:

- Test creating a session and verifying it exists
- Test updating a session and verifying changes
- Test listing sessions
- Test deleting a session

## 4. Implementation Steps

1. **Create Models** (1 day)
   - Implement Pydantic models for session operations
   - Write tests for model validation

2. **Implement Service Layer** (2 days)
   - Implement SessionService with all methods
   - Write tests for service functions

3. **Implement Router** (1 day)
   - Create router with all endpoints
   - Implement endpoint handler functions
   - Connect to service layer

4. **Integration Testing** (1 day)
   - Test the entire flow with the agent manager
   - Verify API contract compliance

5. **Documentation** (1 day)
   - Update API documentation with new endpoints
   - Add examples for each operation

## 5. Dependencies and Required Changes

1. **UItoAgentBridgeManager Changes**
   - We may need to enhance the agent manager to better support:
     - Retrieving detailed information about sessions
     - Listing sessions with pagination
     - Efficiently updating session properties

2. **Integration with Existing Functionality**
   - Ensure proper handling of existing session functionality
   - Make sure session deletion properly cleans up resources

## 6. Expected Outcomes

Upon completion of this step, we'll have a fully functional session management API that allows:

1. Creating new sessions with flexible configuration
2. Listing existing sessions with pagination
3. Retrieving detailed information about a specific session
4. Updating session properties
5. Deleting sessions and properly cleaning up resources

These endpoints will form the foundation for the rest of the session-related functionality in the v2 API.

## 7. Risks and Mitigations

1. **Risk**: Agent manager may not support all operations cleanly
   **Mitigation**: We may need to implement adapter methods in the service layer

2. **Risk**: Session updates may require complex validation
   **Mitigation**: Use Pydantic's validation capabilities and add custom validators

3. **Risk**: Performance issues with session listing
   **Mitigation**: Implement proper pagination and filtering

4. **Risk**: Resource leaks if session cleanup fails
   **Mitigation**: Implement robust error handling and cleanup logging

## 8. Example Requests and Responses

### Create Session
```http
POST /api/v2/sessions HTTP/1.1
Content-Type: application/json

{
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "temperature": 0.7,
  "tools": ["search", "calculator"]
}
```

Response:
```json
{
  "id": "sess_12345",
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "created_at": "2023-05-01T12:00:00Z",
  "last_activity": "2023-05-01T12:00:00Z",
  "agent_internal_id": "agent_67890",
  "tools": ["search", "calculator"],
  "temperature": 0.7,
  "reasoning_effort": null,
  "budget_tokens": null,
  "max_tokens": null,
  "custom_prompt": null
}
```

### List Sessions
```http
GET /api/v2/sessions?limit=10&offset=0 HTTP/1.1
```

Response:
```json
{
  "items": [
    {
      "id": "sess_12345",
      "model_id": "gpt-4",
      "persona_id": "programmer",
      "created_at": "2023-05-01T12:00:00Z",
      "last_activity": "2023-05-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### Get Session
```http
GET /api/v2/sessions/sess_12345 HTTP/1.1
```

Response:
```json
{
  "id": "sess_12345",
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "created_at": "2023-05-01T12:00:00Z",
  "last_activity": "2023-05-01T12:00:00Z",
  "agent_internal_id": "agent_67890",
  "tools": ["search", "calculator"],
  "temperature": 0.7,
  "reasoning_effort": null,
  "budget_tokens": null,
  "max_tokens": null,
  "custom_prompt": null
}
```

### Update Session
```http
PATCH /api/v2/sessions/sess_12345 HTTP/1.1
Content-Type: application/json

{
  "temperature": 0.8,
  "persona_id": "researcher"
}
```

Response:
```json
{
  "id": "sess_12345",
  "model_id": "gpt-4",
  "persona_id": "researcher",
  "created_at": "2023-05-01T12:00:00Z",
  "last_activity": "2023-05-01T12:05:00Z",
  "agent_internal_id": "agent_67890",
  "tools": ["search", "calculator"],
  "temperature": 0.8,
  "reasoning_effort": null,
  "budget_tokens": null,
  "max_tokens": null,
  "custom_prompt": null
}
```

### Delete Session
```http
DELETE /api/v2/sessions/sess_12345 HTTP/1.1
```

Response:
```
HTTP/1.1 204 No Content
```

This detailed plan provides a solid foundation for implementing Phase 3.1: Session CRUD Operations. Once completed, we can move on to implementing the agent configuration management endpoints in Phase 3.2.