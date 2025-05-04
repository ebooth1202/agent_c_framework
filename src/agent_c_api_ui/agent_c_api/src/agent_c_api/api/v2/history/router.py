from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from agent_c_api.core.util.logging_utils import LoggingManager
from .models import HistorySummary, HistoryDetail, PaginationParams, HistoryListResponse
from .services import HistoryService

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()

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
    summary="Get Session History",
    description="Get detailed information about a specific session history."
)
async def get_history(session_id: str):
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
    summary="Delete Session History",
    description="Delete a session history and all its files."
)
async def delete_history(session_id: str):
    """Delete a session history and all its files."""
    try:
        success = await history_service.delete_history(session_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Session history {session_id} not found or could not be deleted"
            )
        return {"status": "success", "message": f"Session history {session_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session history {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session history: {str(e)}")