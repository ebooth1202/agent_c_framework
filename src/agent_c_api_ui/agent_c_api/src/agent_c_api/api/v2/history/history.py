from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import Dict
from fastapi_versioning import version

from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.api.v2.models.history_models import HistoryDetail, PaginationParams, HistoryListResponse
from agent_c_api.api.v2.models.response_models import APIResponse, APIStatus
from .services import HistoryService

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()

router = APIRouter(tags=["history"])
history_service = HistoryService()

@router.get(
    "/",
    response_model=HistoryListResponse,
    summary="List Session Histories",
    description="List all available session histories with pagination and sorting.",
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved session histories",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "name": "Task Planning Session",
                                "created_at": "2025-04-01T14:30:00Z",
                                "updated_at": "2025-04-01T15:45:00Z",
                                "message_count": 24,
                                "duration": 4500
                            },
                            {
                                "session_id": "8c282a4d-1f5e-4dab-b92a-04a24eb8173c",
                                "name": "Code Review Session",
                                "created_at": "2025-04-02T09:15:00Z",
                                "updated_at": "2025-04-02T10:30:00Z",
                                "message_count": 18,
                                "duration": 4200
                            }
                        ],
                        "total": 42,
                        "limit": 20,
                        "offset": 0
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to list session histories: database connection error"
                    }
                }
            }
        }
    }
)
@version(2)
async def list_histories(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of histories to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of histories to skip for pagination"),
    sort_by: str = Query("start_time", description="Field to sort by (e.g., 'start_time', 'name', 'message_count')"),
    sort_order: str = Query("desc", description="Sort order ('asc' for ascending or 'desc' for descending)")
):
    """List all available session histories with pagination and sorting."""
    pagination = PaginationParams(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    try:
        return await history_service.list_histories(pagination)
    except Exception as e:
        logger.error(f"Error listing session histories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list session histories: {str(e)}")

@router.get(
    "/{session_id}",
    response_model=HistoryDetail,
    summary="Get Session History Details",
    description="Get detailed information about a specific session history including event types, file information, and metadata.",
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved session history details",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "Task Planning Session",
                        "created_at": "2025-04-01T14:30:00Z",
                        "updated_at": "2025-04-01T15:45:00Z",
                        "message_count": 24,
                        "duration": 4500,
                        "files": ["events_3fa85f64_1.jsonl", "events_3fa85f64_2.jsonl"],
                        "event_types": {
                            "text_delta": 120,
                            "tool_call": 15,
                            "user_request": 12,
                            "thinking": 30
                        },
                        "metadata": {
                            "model": "gpt-4-turbo",
                            "completion_tokens": 4820,
                            "prompt_tokens": 1650
                        },
                        "user_id": "user_12345",
                        "has_thinking": True,
                        "tool_calls": ["web_search", "file_reader", "code_interpreter"]
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Session history not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session history 3fa85f64-5717-4562-b3fc-2c963f66afa6 not found"
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to retrieve session history: database error"
                    }
                }
            }
        }
    }
)
@version(2)
async def get_history(session_id: str = Path(..., description="Unique identifier of the session history to retrieve")):
    """Get detailed information about a specific session history."""
    try:
        history = await history_service.get_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail=f"Session history {session_id} not found")
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session history {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")

@router.delete(
    "/{session_id}",
    response_model=APIResponse[Dict[str, str]],
    summary="Delete Session History",
    description="Delete a session history and all its associated event files and metadata.",
    responses={
        status.HTTP_200_OK: {
            "description": "Session history successfully deleted",
            "content": {
                "application/json": {
                    "example": {
                        "status": {
                            "success": True,
                            "message": "Session history deleted successfully",
                            "error_code": None
                        },
                        "data": {
                            "status": "success", 
                            "message": "Session history 3fa85f64-5717-4562-b3fc-2c963f66afa6 deleted successfully"
                        }
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Session history not found or could not be deleted",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session history 3fa85f64-5717-4562-b3fc-2c963f66afa6 not found or could not be deleted"
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to delete session history: file system error"
                    }
                }
            }
        }
    }
)
@version(2)
async def delete_history(session_id: str = Path(..., description="Unique identifier of the session history to delete")):
    """Delete a session history and all its files."""
    try:
        success = await history_service.delete_history(session_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Session history {session_id} not found or could not be deleted"
            )
        response_data = {"status": "success", "message": f"Session history {session_id} deleted successfully"}
        return APIResponse(
            status=APIStatus(success=True, message="Session history deleted successfully"),
            data=response_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session history {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session history: {str(e)}")