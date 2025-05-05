# Agent C API V2 - Implementation Step 4.2: Event Access (Revised Plan)

## Overview

This document outlines our revised plan for implementing Phase 4.2: Event Access. This plan now properly takes into account the existing models in `api/v2/models`.

## Step Analysis

### What Are We Changing?

We're implementing new v2 API endpoints for event access that will:

1. Retrieve events for a specific session with various filtering options
2. Stream events for a session with optional real-time timing
3. Control session replay (play, pause, stop, seek)
4. Get the current status of a session replay

These endpoints will replace the v1 `/events` endpoints with more RESTful and consistent v2 endpoints under the history namespace.

### How Are We Changing It?

We'll create new routes and services for the v2 API while reusing the core business logic from the v1 implementation and **leveraging existing v2 models**. Specifically:

1. Create RESTful endpoints under `/api/v2/history/{session_id}/events`
2. Add streaming endpoint at `/api/v2/history/{session_id}/stream`
3. Add replay control endpoints at `/api/v2/history/{session_id}/replay`
4. Implement an `EventService` that leverages the existing v1 EventService functionality
5. Use the existing models from `api/v2/models/history_models.py` and `api/v2/models/response_models.py`
6. Enhance filtering capabilities and error handling
7. Add comprehensive tests for the new endpoints

### Why Are We Changing It?

The redesign offers several advantages:

1. More intuitive and RESTful API structure (events as a sub-resource of sessions)
2. Improved consistency with the rest of the v2 API
3. Enhanced filtering capabilities and documentation
4. Better organization of replay controls into a dedicated set of endpoints

## Implementation Details

### 1. Use Existing Models

We'll use the following existing models from `api/v2/models/history_models.py`:

- `Event`: Represents a recorded event in session history
- `EventFilter`: Parameters for filtering history events
- `ReplayStatus`: Status of a session replay
- `ReplayControl`: Parameters for controlling replay

And we'll use these models from `api/v2/models/response_models.py`:

- `APIResponse`: Standard API response wrapper
- `PaginatedResponse`: Paginated response wrapper

### 2. Service Implementation

Create a new service in `api/v2/history/services.py` by extending the existing file:

```python
# Add imports at the top of the file
from agent_c_api.api.v1.interactions.services.event_service import EventService as V1EventService
from agent_c_api.api.v2.models.history_models import Event, EventFilter, ReplayStatus, ReplayControl
from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, PaginationMeta, APIStatus
from uuid import UUID
from datetime import datetime

# Add to existing services.py file after HistoryService

class EventService:
    def __init__(self):
        self._event_service = V1EventService()
    
    async def get_events(
        self, 
        session_id: UUID, 
        filter_params: EventFilter
    ) -> PaginatedResponse[Event]:
        """Get events for a specific session with filtering"""
        # Convert UUID to string for v1 service
        session_id_str = str(session_id)
        
        v1_events = await self._event_service.get_events(
            session_id=session_id_str,
            event_types=filter_params.event_types,
            start_time=filter_params.start_time.isoformat() if filter_params.start_time else None,
            end_time=filter_params.end_time.isoformat() if filter_params.end_time else None,
            limit=filter_params.limit
        )
        
        # Convert to v2 Event model format
        v2_events = [
            Event(
                id=f"{session_id_str}-{i}",  # Generate an ID if v1 doesn't provide one
                session_id=session_id,
                timestamp=e.timestamp,
                event_type=e.type.value,  # Convert enum to string
                data={
                    "role": e.role,
                    "content": e.content,
                    "format": e.format,
                    "running": e.running,
                    "active": e.active,
                    "vendor": e.vendor,
                    "tool_calls": e.tool_calls,
                    "tool_results": e.tool_results,
                    "raw": e.raw
                }
            ) for i, e in enumerate(v1_events)
        ]
        
        # Create pagination metadata
        pagination = PaginationMeta(
            page=1,  # Since v1 doesn't support pagination, we're always on page 1
            page_size=filter_params.limit,
            total_items=len(v2_events),
            total_pages=1
        )
        
        return PaginatedResponse(
            status=APIStatus(success=True),
            data=v2_events,
            pagination=pagination
        )
    
    def stream_events(
        self, 
        session_id: UUID, 
        event_types: Optional[List[str]] = None,
        real_time: bool = False,
        speed_factor: float = 1.0
    ):
        """Stream events for a session, optionally with real-time timing"""
        # Convert UUID to string and event types to v1 format if needed
        session_id_str = str(session_id)
        
        # Map event types to v1 format if needed
        # This is a simplification - actual implementation would need to map
        # between v2 event type strings and v1 EventType enum
        
        return self._event_service.stream_events(
            session_id=session_id_str,
            event_types=event_types,  # Simplified - may need conversion
            real_time=real_time,
            speed_factor=speed_factor
        )
    
    def get_replay_status(self, session_id: UUID) -> Optional[ReplayStatus]:
        """Get the current status of a session replay"""
        session_id_str = str(session_id)
        status = self._event_service.get_replay_status(session_id_str)
        if not status:
            return None
        
        # Convert v1 status format to v2 ReplayStatus
        # This mapping would need to be adjusted based on actual v1 format
        return ReplayStatus(
            session_id=session_id,
            is_playing=status.get("state", "") == "playing",
            current_position=datetime.fromisoformat(status.get("position")) if status.get("position") else datetime.now(),
            start_time=datetime.now() - timedelta(hours=1),  # Placeholder - get from actual data
            end_time=datetime.now()  # Placeholder - get from actual data
        )
    
    async def control_replay(
        self, 
        session_id: UUID, 
        control: ReplayControl,
        background_tasks = None
    ) -> APIResponse[bool]:
        """Control a session replay (play, pause, stop, seek)"""
        session_id_str = str(session_id)
        
        # Map v2 action to v1 format
        # Note: v1 supports "stop" which v2 doesn't (based on the model)
        action = control.action
        position = control.position.isoformat() if control.position else None
        
        result = await self._event_service.control_replay(
            session_id=session_id_str,
            action=action,
            position=position,
            background_tasks=background_tasks
        )
        
        return APIResponse(
            status=APIStatus(
                success=result,
                message=f"Replay control '{action}' {'successful' if result else 'failed'}",
                error_code=None if result else "REPLAY_CONTROL_FAILED"
            ),
            data=result
        )
```

### 3. Router Implementation

Create a new router in `api/v2/history/hsitory.py`:

```python
from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.api.v2.models.history_models import Event, EventFilter, ReplayStatus, ReplayControl
from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse
from .services import EventService

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()

router = APIRouter()
event_service = EventService()

@router.get(
    "/{session_id}/events",
    response_model=PaginatedResponse[Event],
    summary="Get Session Events",
    description="Get events for a specific session with filtering options."
)
async def get_events(
    session_id: UUID = Path(..., description="Session ID"),
    event_types: Optional[List[str]] = Query(None, description="Filter by event types"),
    start_time: Optional[datetime] = Query(None, description="Filter events after this timestamp"),
    end_time: Optional[datetime] = Query(None, description="Filter events before this timestamp"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return")
):
    """Get events for a specific session with filtering options."""
    filter_params = EventFilter(
        event_types=event_types,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    
    try:
        events_response = await event_service.get_events(session_id, filter_params)
        if not events_response.data:
            raise HTTPException(status_code=404, detail=f"No events found for session {session_id}")
        return events_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving events for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")

@router.get(
    "/{session_id}/stream",
    summary="Stream Session Events",
    description="Stream events for a session, optionally in real-time."
)
async def stream_events(
    session_id: UUID = Path(..., description="Session ID"),
    event_types: Optional[List[str]] = Query(None, description="Filter by event types"),
    real_time: bool = Query(False, description="Replay events with original timing"),
    speed_factor: float = Query(1.0, ge=0.1, le=10.0, description="Speed multiplier for real-time replay")
):
    """Stream events for a session, optionally in real-time."""
    try:
        event_stream = event_service.stream_events(
            session_id=session_id,
            event_types=event_types,
            real_time=real_time,
            speed_factor=speed_factor
        )
        return StreamingResponse(
            event_stream,
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error streaming events for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stream events: {str(e)}")

@router.get(
    "/{session_id}/replay",
    response_model=APIResponse[ReplayStatus],
    summary="Get Replay Status",
    description="Get the current status of a session replay."
)
async def get_replay_status(session_id: UUID = Path(..., description="Session ID")):
    """Get the current status of a session replay."""
    try:
        status = event_service.get_replay_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"No active replay for session {session_id}")
        
        return APIResponse(
            status=APIStatus(success=True),
            data=status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting replay status for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get replay status: {str(e)}")

@router.post(
    "/{session_id}/replay",
    response_model=APIResponse[bool],
    summary="Control Replay",
    description="Control a session replay (play, pause, seek)."
)
async def control_replay(
    control: ReplayControl,
    session_id: UUID = Path(..., description="Session ID"),
    background_tasks: BackgroundTasks = None
):
    """Control a session replay (play, pause, seek)."""
    try:
        result = await event_service.control_replay(
            session_id=session_id,
            control=control,
            background_tasks=background_tasks
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error controlling replay for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to control replay: {str(e)}")
```

### 4. Router Integration

Update `api/v2/history/__init__.py` to include the new events router (same as in the original plan):

```python
from fastapi import APIRouter
from .history import router as history_router
from .events import router as events_router

router = APIRouter(prefix="/history")
router.include_router(history_router)
router.include_router(events_router)
```

### 5. Test Implementation

Create tests in `tests/v2/history/test_events.py`, adapting to use the correct models from `api/v2/models/history_models.py`:

```python
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.responses import StreamingResponse
from uuid import UUID, uuid4

from agent_c_api.api.v2.history.services import EventService
from agent_c_api.api.v2.models.history_models import Event, EventFilter, ReplayStatus, ReplayControl
from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, PaginationMeta, APIStatus

# Test data
session_id = uuid4()

MOCK_EVENTS = [
    Event(
        id=f"{session_id}-1",
        session_id=session_id,
        timestamp=datetime.now() - timedelta(minutes=5),
        event_type="user_request",
        data={
            "role": "user",
            "content": "Hello, agent",
            "raw": {"original": "data"}
        }
    ),
    Event(
        id=f"{session_id}-2",
        session_id=session_id,
        timestamp=datetime.now() - timedelta(minutes=4),
        event_type="text_delta",
        data={
            "role": "assistant",
            "content": "Hello, user",
            "raw": {"original": "data"}
        }
    )
]

MOCK_REPLAY_STATUS = ReplayStatus(
    session_id=session_id,
    is_playing=True,
    current_position=datetime.now() - timedelta(minutes=4),
    start_time=datetime.now() - timedelta(minutes=10),
    end_time=datetime.now()
)

@pytest.mark.asyncio
@patch.object(EventService, "get_events")
async def test_get_events(mock_get_events, client):
    # Setup mock
    mock_response = PaginatedResponse(
        status=APIStatus(success=True),
        data=MOCK_EVENTS,
        pagination=PaginationMeta(
            page=1,
            page_size=100,
            total_items=len(MOCK_EVENTS),
            total_pages=1
        )
    )
    mock_get_events.return_value = mock_response
    
    # Test endpoint
    response = client.get(f"/api/v2/history/{session_id}/events")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"]["success"] == True
    assert len(data["data"]) == len(MOCK_EVENTS)
    assert data["data"][0]["event_type"] == "user_request"

@pytest.mark.asyncio
@patch.object(EventService, "get_events")
async def test_get_events_with_filters(mock_get_events, client):
    # Setup mock with filtered data
    filtered_events = [MOCK_EVENTS[0]]  # Just the user_request
    mock_response = PaginatedResponse(
        status=APIStatus(success=True),
        data=filtered_events,
        pagination=PaginationMeta(
            page=1,
            page_size=10,
            total_items=len(filtered_events),
            total_pages=1
        )
    )
    mock_get_events.return_value = mock_response
    
    # Test endpoint with filters
    response = client.get(f"/api/v2/history/{session_id}/events?event_types=user_request&limit=10")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["event_type"] == "user_request"

@pytest.mark.asyncio
@patch.object(EventService, "get_events")
async def test_get_events_not_found(mock_get_events, client):
    # Setup mock for empty results
    mock_response = PaginatedResponse(
        status=APIStatus(success=True),
        data=[],
        pagination=PaginationMeta(
            page=1,
            page_size=100,
            total_items=0,
            total_pages=0
        )
    )
    mock_get_events.return_value = mock_response
    
    # Test endpoint
    response = client.get(f"/api/v2/history/{uuid4()}/events")
    
    # Verify response
    assert response.status_code == 404
    assert "No events found" in response.json()["detail"]

@pytest.mark.asyncio
@patch.object(EventService, "stream_events")
async def test_stream_events(mock_stream_events, client):
    # Setup mock
    async def mock_event_generator():
        for i in range(3):
            yield f"data: {i}\n\n"
    
    mock_stream_events.return_value = mock_event_generator()
    
    # Test endpoint
    response = client.get(f"/api/v2/history/{session_id}/stream")
    
    # Verify it's a streaming response
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

@pytest.mark.asyncio
@patch.object(EventService, "get_replay_status")
async def test_get_replay_status(mock_get_replay_status, client):
    # Setup mock
    mock_get_replay_status.return_value = MOCK_REPLAY_STATUS
    
    # Test endpoint
    response = client.get(f"/api/v2/history/{session_id}/replay")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"]["success"] == True
    assert data["data"]["session_id"] == str(session_id)
    assert data["data"]["is_playing"] == True

@pytest.mark.asyncio
@patch.object(EventService, "get_replay_status")
async def test_get_replay_status_not_found(mock_get_replay_status, client):
    # Setup mock
    mock_get_replay_status.return_value = None
    
    # Test endpoint
    response = client.get(f"/api/v2/history/{uuid4()}/replay")
    
    # Verify response
    assert response.status_code == 404
    assert "No active replay" in response.json()["detail"]

@pytest.mark.asyncio
@patch.object(EventService, "control_replay")
async def test_control_replay(mock_control_replay, client):
    # Setup mock
    mock_response = APIResponse(
        status=APIStatus(success=True, message="Replay control successful"),
        data=True
    )
    mock_control_replay.return_value = mock_response
    
    # Test endpoint
    response = client.post(
        f"/api/v2/history/{session_id}/replay",
        json={"action": "play"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"]["success"] == True
    assert data["data"] == True

@pytest.mark.asyncio
@patch.object(EventService, "control_replay")
async def test_control_replay_invalid(mock_control_replay, client):
    # Setup mock
    mock_response = APIResponse(
        status=APIStatus(success=False, message="Replay control failed", error_code="REPLAY_CONTROL_FAILED"),
        data=False
    )
    mock_control_replay.return_value = mock_response
    
    # Test endpoint
    response = client.post(
        f"/api/v2/history/{session_id}/replay",
        json={"action": "pause"}
    )
    
    # Verify response
    assert response.status_code == 200  # Still returns 200 but with success=False
    data = response.json()
    assert data["status"]["success"] == False
    assert data["status"]["error_code"] == "REPLAY_CONTROL_FAILED"
```

### 6. Documentation

Update API documentation in `docs/api_v2/history.md` to include the event endpoints (same as before but adapted to match the actual models used).

## Implementation Tasks

1. **Use Existing Models**
   - Use models from `api/v2/models/history_models.py` and `api/v2/models/response_models.py`
   - Ensure proper validation and documentation for all fields

2. **Implement Event Service**
   - Add the `EventService` class to the existing `api/v2/history/services.py`
   - Ensure proper error handling and conversion between v1 and v2 models

3. **Create Events Router**
   - Implement the router in a new `api/v2/history/events.py` file
   - Add proper error handling and validation

4. **Update Router Integration**
   - Update `api/v2/history/__init__.py` to include the events router

5. **Write Tests**
   - Implement tests for all endpoints and service methods
   - Cover both success and error cases

6. **Add Documentation**
   - Update the history documentation with event endpoints

## Testing Strategy

We'll test the event endpoints by:

1. Mocking the service layer to isolate endpoint behavior
2. Testing filtering functionality with various parameters
3. Verifying streaming response format and headers
4. Testing replay control with different actions
5. Verifying error responses for invalid inputs

## Estimated Effort

- Service implementation: 2-3 hours
- Router implementation: 1-2 hours
- Tests: 2-3 hours
- Documentation: 1 hour
- Total: 6-9 hours