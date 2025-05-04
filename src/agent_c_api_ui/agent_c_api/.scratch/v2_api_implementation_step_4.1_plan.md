# Agent C API V2 - Implementation Step 4.1: Session History Management

## Overview

This document outlines our plan for implementing Phase 4.1: Session History Management from our implementation plan. This step focuses on creating RESTful endpoints for listing and accessing session histories while leveraging existing interaction service logic.

## Step Analysis

### What Are We Changing?

We're implementing new v2 API endpoints for session history management that will:

1. List available session histories with pagination and filtering
2. Retrieve detailed information about a specific session history
3. Delete session history data

These endpoints will replace the v1 `/interactions` endpoints with more RESTful and consistent v2 endpoints.

### How Are We Changing It?

We'll create new routes, models, and services for the v2 API while reusing the core business logic from the v1 implementation. Specifically:

1. Create RESTful endpoints under `/api/v2/history`
2. Create appropriate Pydantic models for request/response validation
3. Implement a `HistoryService` that leverages the existing `InteractionService` functionality
4. Enhance error handling and validation
5. Add comprehensive tests for the new endpoints

### Why Are We Changing It?

The redesign offers several advantages:

1. Provides a more intuitive and RESTful API structure
2. Improves consistency with the rest of the v2 API
3. Enhances documentation and client usability
4. Maintains the robust underlying implementation while improving the interface

## Implementation Details

### 1. Model Definitions

Implement the following models in `api/v2/history/models.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional

class HistorySummary(BaseModel):
    """Summary of a recorded session history"""
    id: str = Field(..., description="Session ID")
    start_time: datetime = Field(..., description="When the session started")
    end_time: Optional[datetime] = Field(None, description="When the session ended")
    duration_seconds: Optional[float] = Field(None, description="Session duration in seconds")
    event_count: int = Field(..., description="Number of events in the session")
    file_count: int = Field(..., description="Number of log files for the session")

class HistoryDetail(HistorySummary):
    """Detailed information about a session history"""
    files: List[str] = Field(..., description="List of log files for the session")
    event_types: Dict[str, int] = Field(..., description="Count of each event type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")
    user_id: Optional[str] = Field(None, description="User ID associated with the session")
    has_thinking: bool = Field(False, description="Whether the session includes thinking events")
    tool_calls: List[str] = Field([], description="List of tools used in the session")

class PaginationParams(BaseModel):
    """Parameters for pagination"""
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("start_time", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc or desc)")

class HistoryListResponse(BaseModel):
    """Response for listing session histories"""
    items: List[HistorySummary] = Field(..., description="List of session histories")
    total: int = Field(..., description="Total number of session histories")
    limit: int = Field(..., description="Maximum number of results returned")
    offset: int = Field(..., description="Number of results skipped")
```

### 2. Service Implementation

Create a `HistoryService` class in `api/v2/history/services.py` that wraps the existing `InteractionService`:

```python
from typing import List, Optional, Dict, Any
from agent_c_api.api.v1.interactions.services.interaction_service import InteractionService
from .models import HistorySummary, HistoryDetail, PaginationParams

class HistoryService:
    def __init__(self):
        self._interaction_service = InteractionService()
    
    async def list_histories(self, pagination: PaginationParams) -> Dict[str, Any]:
        """List available session histories with pagination"""
        histories = await self._interaction_service.list_sessions(
            limit=pagination.limit,
            offset=pagination.offset,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order
        )
        
        # Convert to HistorySummary objects
        history_summaries = [HistorySummary(
            id=h.id,
            start_time=h.start_time,
            end_time=h.end_time,
            duration_seconds=h.duration_seconds,
            event_count=h.event_count,
            file_count=h.file_count
        ) for h in histories]
        
        # Get total count (this could be optimized in future)
        total_histories = len(await self._interaction_service.list_sessions(
            limit=1000000,  # Effectively no limit
            offset=0,
            sort_by="start_time",
            sort_order="desc"
        ))
        
        return {
            "items": history_summaries,
            "total": total_histories,
            "limit": pagination.limit,
            "offset": pagination.offset
        }
    
    async def get_history(self, session_id: str) -> Optional[HistoryDetail]:
        """Get detailed information about a specific session history"""
        session = await self._interaction_service.get_session(session_id)
        if not session:
            return None
            
        return HistoryDetail(
            id=session.id,
            start_time=session.start_time,
            end_time=session.end_time,
            duration_seconds=session.duration_seconds,
            event_count=session.event_count,
            file_count=session.file_count,
            files=session.files,
            event_types=session.event_types,
            metadata=session.metadata,
            user_id=session.user_id,
            has_thinking=session.has_thinking,
            tool_calls=session.tool_calls
        )
    
    async def delete_history(self, session_id: str) -> bool:
        """Delete a session history"""
        return await self._interaction_service.delete_session(session_id)
```

### 3. Router Implementation

Create a new router in `api/v2/history/history.py`:

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from .models import HistorySummary, HistoryDetail, PaginationParams, HistoryListResponse
from .services import HistoryService

router = APIRouter(tags=["history"])
history_service = HistoryService()

@router.get(
    "",
    response_model=HistoryListResponse,
    summary="List Session Histories",
    description="List all available session histories with pagination and sorting."
)
async def list_histories(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of histories to return"),
    offset: int = Query(0, ge=0, description="Number of histories to skip"),
    sort_by: str = Query("start_time", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)")
):
    pagination = PaginationParams(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await history_service.list_histories(pagination)

@router.get(
    "/{session_id}",
    response_model=HistoryDetail,
    summary="Get Session History",
    description="Get detailed information about a specific session history."
)
async def get_history(session_id: str):
    history = await history_service.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"Session history {session_id} not found")
    return history

@router.delete(
    "/{session_id}",
    summary="Delete Session History",
    description="Delete a session history and all its files."
)
async def delete_history(session_id: str):
    success = await history_service.delete_history(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session history {session_id} not found or could not be deleted")
    return {"status": "success", "message": f"Session history {session_id} deleted successfully"}
```

### 4. Router Integration

Update `api/v2/history/__init__.py` to include the new router:

```python
from fastapi import APIRouter
from .history import router as history_router

router = APIRouter(prefix="/history")
router.include_router(history_router)
```

Update the main v2 router in `api/v2/__init__.py` to include the history router (if not already included):

```python
# Ensure this import is uncommented
from .history import router as history_router

# Ensure this line is uncommented
router.include_router(history_router)
```

### 5. Test Implementation

Create tests in `tests/v2/history/test_history.py`:

```python
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from agent_c_api.api.v2.history.services import HistoryService

# Test data
MOCK_HISTORY_SUMMARIES = [
    {
        "id": "session1",
        "start_time": datetime.now() - timedelta(hours=2),
        "end_time": datetime.now() - timedelta(hours=1),
        "duration_seconds": 3600,
        "event_count": 120,
        "file_count": 2
    },
    {
        "id": "session2",
        "start_time": datetime.now() - timedelta(hours=4),
        "end_time": datetime.now() - timedelta(hours=3),
        "duration_seconds": 3600,
        "event_count": 80,
        "file_count": 1
    }
]

MOCK_HISTORY_DETAIL = {
    "id": "session1",
    "start_time": datetime.now() - timedelta(hours=2),
    "end_time": datetime.now() - timedelta(hours=1),
    "duration_seconds": 3600,
    "event_count": 120,
    "file_count": 2,
    "files": ["events_1.jsonl", "events_2.jsonl"],
    "event_types": {"text_delta": 80, "tool_call": 10, "user_request": 5},
    "metadata": {"model": "gpt-4"},
    "user_id": "user123",
    "has_thinking": True,
    "tool_calls": ["tool1", "tool2"]
}

@pytest.mark.asyncio
@patch.object(HistoryService, "list_histories")
async def test_list_histories(mock_list_histories, client: AsyncClient):
    # Setup mock
    mock_response = {
        "items": MOCK_HISTORY_SUMMARIES,
        "total": len(MOCK_HISTORY_SUMMARIES),
        "limit": 50,
        "offset": 0
    }
    mock_list_histories.return_value = mock_response
    
    # Test endpoint
    response = await client.get("/api/v2/history")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(MOCK_HISTORY_SUMMARIES)
    assert len(data["items"]) == len(MOCK_HISTORY_SUMMARIES)
    assert data["items"][0]["id"] == "session1"

@pytest.mark.asyncio
@patch.object(HistoryService, "get_history")
async def test_get_history(mock_get_history, client: AsyncClient):
    # Setup mock
    mock_get_history.return_value = MOCK_HISTORY_DETAIL
    
    # Test endpoint
    response = await client.get("/api/v2/history/session1")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "session1"
    assert data["event_count"] == 120
    assert len(data["files"]) == 2
    assert "tool1" in data["tool_calls"]

@pytest.mark.asyncio
@patch.object(HistoryService, "get_history")
async def test_get_history_not_found(mock_get_history, client: AsyncClient):
    # Setup mock
    mock_get_history.return_value = None
    
    # Test endpoint
    response = await client.get("/api/v2/history/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@pytest.mark.asyncio
@patch.object(HistoryService, "delete_history")
async def test_delete_history(mock_delete_history, client: AsyncClient):
    # Setup mock
    mock_delete_history.return_value = True
    
    # Test endpoint
    response = await client.delete("/api/v2/history/session1")
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
@patch.object(HistoryService, "delete_history")
async def test_delete_history_not_found(mock_delete_history, client: AsyncClient):
    # Setup mock
    mock_delete_history.return_value = False
    
    # Test endpoint
    response = await client.delete("/api/v2/history/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
```

### 6. Documentation

Create API documentation in `docs/api_v2/history.md`:

```markdown
# History API

The History API provides access to session histories and their events. This allows you to list available session histories, retrieve details about specific sessions, and manage history data.

## Endpoints

### List Session Histories

```
GET /api/v2/history
```

Lists all available session histories with pagination and sorting options.

#### Query Parameters

- `limit` (integer, default: 50): Maximum number of histories to return (1-100)
- `offset` (integer, default: 0): Number of histories to skip
- `sort_by` (string, default: "start_time"): Field to sort by
- `sort_order` (string, default: "desc"): Sort order ("asc" or "desc")

#### Response

```json
{
  "items": [
    {
      "id": "string",
      "start_time": "2023-01-01T12:00:00Z",
      "end_time": "2023-01-01T12:30:00Z",
      "duration_seconds": 1800,
      "event_count": 120,
      "file_count": 2
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

### Get Session History Details

```
GET /api/v2/history/{session_id}
```

Retrieve detailed information about a specific session history.

#### Path Parameters

- `session_id` (string, required): The ID of the session

#### Response

```json
{
  "id": "string",
  "start_time": "2023-01-01T12:00:00Z",
  "end_time": "2023-01-01T12:30:00Z",
  "duration_seconds": 1800,
  "event_count": 120,
  "file_count": 2,
  "files": ["events_1.jsonl", "events_2.jsonl"],
  "event_types": {
    "text_delta": 80,
    "tool_call": 10,
    "user_request": 5
  },
  "metadata": {
    "model": "gpt-4"
  },
  "user_id": "user123",
  "has_thinking": true,
  "tool_calls": ["tool1", "tool2"]
}
```

#### Error Responses

- `404 Not Found`: Session history not found

### Delete Session History

```
DELETE /api/v2/history/{session_id}
```

Delete a session history and all its files.

#### Path Parameters

- `session_id` (string, required): The ID of the session to delete

#### Response

```json
{
  "status": "success",
  "message": "Session history session1 deleted successfully"
}
```

#### Error Responses

- `404 Not Found`: Session history not found or could not be deleted
```

## Implementation Tasks

1. **Create Models**
   - Implement Pydantic models in `api/v2/history/models.py`
   - Ensure proper validation and documentation

2. **Implement Service**
   - Create the HistoryService class that leverages the existing InteractionService
   - Implement list, get, and delete methods

3. **Create Router**
   - Implement the router with list, get, and delete endpoints
   - Add proper error handling

4. **Update Router Integration**
   - Update `__init__.py` files to include the history router

5. **Write Tests**
   - Implement tests for all endpoints
   - Cover both success and error cases

6. **Add Documentation**
   - Create comprehensive documentation for the history API

## Testing Strategy

We'll test the history endpoints by:

1. Mocking the service layer to isolate endpoint behavior
2. Testing pagination and sorting functionality
3. Verifying error responses for invalid inputs
4. Testing edge cases like empty history lists

## Estimated Effort

- Core implementation: 2-3 hours
- Tests: 1-2 hours
- Documentation: 1 hour
- Total: 4-6 hours