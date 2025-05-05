from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from fastapi_versioning import version
from starlette import status

from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.api.v2.models.history_models import StoredEvent, HistoryEventUnion, EventFilter, ReplayStatus, ReplayControl
from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, APIStatus
from .services import EventService

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()

router = APIRouter(tags=["history"])
event_service = EventService()

@router.get(
    "/{session_id}/events",
    response_model=PaginatedResponse[StoredEvent],
    summary="Get Session Events",
    description="""
    Get events for a specific session with filtering options.
    
    This endpoint allows retrieving the full event history of a session with
    flexible filtering options. Events can be filtered by type, time range,
    and limited to control response size. The response is paginated to handle
    large event histories efficiently.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved session events",
            "content": {
                "application/json": {
                    "example": {
                        "status": {
                            "success": True,
                            "message": None,
                            "error_code": None
                        },
                        "data": [
                            {
                                "id": "evt_1234567890",
                                "timestamp": "2025-04-01T14:32:15Z",
                                "event": {
                                    "event_type": "message",
                                    "role": "user",
                                    "content": "Can you help me analyze this dataset?",
                                    "message_id": "msg_abcdef123456"
                                }
                            },
                            {
                                "id": "evt_0987654321",
                                "timestamp": "2025-04-01T14:35:42Z",
                                "event": {
                                    "event_type": "tool_call",
                                    "tool_name": "data_analysis",
                                    "input": {
                                        "file_path": "data.csv",
                                        "operation": "summary_statistics"
                                    },
                                    "call_id": "call_defabc456789"
                                }
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "page_size": 50,
                            "total_items": 120,
                            "total_pages": 3
                        }
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No events found for session",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "No events found for session 3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "error_code": "EVENTS_NOT_FOUND",
                            "message": "No events could be found for the specified session"
                        }
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to retrieve events",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Failed to retrieve events: data store error",
                            "error_code": "EVENTS_RETRIEVAL_ERROR",
                            "message": "Error retrieving events for session 3fa85f64-5717-4562-b3fc-2c963f66afa6"
                        }
                    }
                }
            }
        }
    }
)
@version(2)
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
    description="""
    Stream events for a session, optionally in real-time.
    
    This endpoint returns a Server-Sent Events (SSE) stream of session events.
    It can be used to watch event history in real-time (with original timing),
    or as fast as possible. The stream format follows the standard SSE format
    with each event containing JSON data for the specific event type.
    
    The real-time option is particularly useful for replaying sessions with
    original timing, while the non-real-time option is better for quickly
    scanning through session history.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully streaming session events",
            "content": {
                "text/event-stream": {
                    "example": "data: {\"id\":\"evt_1234567890\",\"timestamp\":\"2025-04-01T14:32:15Z\",\"event\":{\"event_type\":\"message\",\"role\":\"user\",\"content\":\"Can you help me analyze this dataset?\",\"message_id\":\"msg_abcdef123456\"}}\n\n"
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to stream events",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Failed to stream events: stream initialization error",
                            "error_code": "STREAM_ERROR",
                            "message": "Error streaming events for session 3fa85f64-5717-4562-b3fc-2c963f66afa6"
                        }
                    }
                }
            }
        }
    }
)
@version(2)
async def stream_events(
    session_id: UUID = Path(..., description="Unique identifier of the session to stream events from"),
    event_types: Optional[List[str]] = Query(None, description="Filter stream to only include these event types (e.g., 'text_delta', 'tool_call', 'thinking')"),
    real_time: bool = Query(False, description="When True, replays events with original timing; when false, streams as fast as possible"),
    speed_factor: float = Query(1.0, ge=0.1, le=10.0, description="Speed multiplier for real-time replay (0.1-10.0, where 1.0 is original speed)")
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
    description="""
    Get the current status of a session replay.
    
    This endpoint returns information about an active replay session,
    including whether it's currently playing, the current position in the timeline,
    and the total time range covered by the session. This can be used to build
    replay control UIs that show progress and allow seeking within the timeline.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved replay status",
            "content": {
                "application/json": {
                    "example": {
                        "status": {
                            "success": True,
                            "message": None,
                            "error_code": None
                        },
                        "data": {
                            "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "is_playing": True,
                            "current_position": "2025-04-01T14:40:15Z",
                            "start_time": "2025-04-01T14:30:00Z",
                            "end_time": "2025-04-01T15:45:00Z"
                        }
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No active replay for the session",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "No active replay for session 3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "error_code": "REPLAY_NOT_FOUND",
                            "message": "No active replay exists for the specified session"
                        }
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to get replay status",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Failed to get replay status: state error",
                            "error_code": "REPLAY_STATUS_ERROR",
                            "message": "Error getting replay status for session 3fa85f64-5717-4562-b3fc-2c963f66afa6"
                        }
                    }
                }
            }
        }
    }
)
@version(2)
async def get_replay_status(session_id: UUID = Path(..., description="Unique identifier of the session to get replay status for")):
    """Get the current status of a session replay."""
    try:
        replay_status = event_service.get_replay_status(session_id)
        if not replay_status:
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
            data=replay_status
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
    description="""
    Control a session replay (play, pause, seek).
    
    This endpoint allows controlling the playback of session replays.
    It supports three main actions:
    
    - **play**: Start or resume playback, optionally at a specific speed
    - **pause**: Pause the current playback
    - **seek**: Jump to a specific position in the timeline
    
    The speed parameter (0.1-10.0) allows for slowing down or speeding up the replay,
    which can be useful for detailed analysis or quick scanning of a session.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully controlled replay",
            "content": {
                "application/json": {
                    "examples": {
                        "play": {
                            "summary": "Response when starting playback",
                            "value": {
                                "status": {
                                    "success": True,
                                    "message": "Replay control 'play' successful",
                                    "error_code": None
                                },
                                "data": True
                            }
                        },
                        "pause": {
                            "summary": "Response when pausing playback",
                            "value": {
                                "status": {
                                    "success": True,
                                    "message": "Replay control 'pause' successful",
                                    "error_code": None
                                },
                                "data": True
                            }
                        },
                        "seek": {
                            "summary": "Response when seeking to position",
                            "value": {
                                "status": {
                                    "success": True,
                                    "message": "Replay control 'seek' successful",
                                    "error_code": None
                                },
                                "data": True
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid replay control parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Missing required 'position' parameter for 'seek' action"
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to control replay",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Failed to control replay: state machine error",
                            "error_code": "REPLAY_CONTROL_ERROR",
                            "message": "Error controlling replay for session 3fa85f64-5717-4562-b3fc-2c963f66afa6"
                        }
                    }
                }
            }
        }
    }
)
@version(2)
async def control_replay(
    control: ReplayControl,
    background_tasks: BackgroundTasks,
    session_id: UUID = Path(..., description="Unique identifier of the session to control replay for"),

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