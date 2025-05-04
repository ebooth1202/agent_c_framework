from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_versioning import version

from agent_c_api.api.v2.models.session_models import SessionCreate, SessionDetail, SessionListResponse, SessionUpdate
from .services import SessionService


def get_session_service():
    """Dependency to get the session service"""
    return SessionService()


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
    try:
        return await service.update_session(session_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")


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