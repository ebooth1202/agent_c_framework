from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.api.v2.models.history_models import Event, EventFilter, ReplayStatus, ReplayControl
from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, APIStatus
from .services import EventService

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()

router = APIRouter(tags=["history"])
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
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": f"No events found for session {session_id}",
                    "error_code": "EVENTS_NOT_FOUND",
                    "message": f"No events could be found for the specified session"
                }
            )
        return events_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving events for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Failed to retrieve events: {str(e)}",
                "error_code": "EVENTS_RETRIEVAL_ERROR",
                "message": f"Error retrieving events for session {session_id}"
            }
        )

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
        # Get the event generator (already returns AsyncGenerator)
        # No need to await it as StreamingResponse expects the generator itself
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
        # Provide empty values for error_code and message to prevent unfilled parameter errors
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Failed to stream events: {str(e)}",
                "error_code": "STREAM_ERROR",
                "message": f"Error streaming events for session {session_id}"
            }
        )

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
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": f"No active replay for session {session_id}",
                    "error_code": "REPLAY_NOT_FOUND",
                    "message": f"No active replay exists for the specified session"
                }
            )
        
        return APIResponse(
            status=APIStatus(success=True),
            data=status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting replay status for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Failed to get replay status: {str(e)}",
                "error_code": "REPLAY_STATUS_ERROR",
                "message": f"Error getting replay status for session {session_id}"
            }
        )

@router.post(
    "/{session_id}/replay",
    response_model=APIResponse[bool],
    summary="Control Replay",
    description="Control a session replay (play, pause, seek)."
)
async def control_replay(
    control: ReplayControl,
    session_id: UUID = Path(..., description="Session ID"),
    background_tasks: BackgroundTasks = Depends()
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
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Failed to control replay: {str(e)}",
                "error_code": "REPLAY_CONTROL_ERROR",
                "message": f"Error controlling replay for session {session_id}"
            }
        )