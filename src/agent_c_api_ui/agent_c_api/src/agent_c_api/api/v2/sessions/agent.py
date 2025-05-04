from fastapi import APIRouter, Depends, HTTPException
from fastapi_versioning import version

from agent_c_api.api.v2.sessions.models import AgentConfig, AgentUpdate, AgentUpdateResponse
from agent_c_api.api.v2.sessions.services import SessionService


def get_session_service():
    """Dependency to get the session service"""
    return SessionService()


router = APIRouter(tags=["agent"])


@router.get("/{session_id}/agent", response_model=AgentConfig)
@version(2)
async def get_agent_config(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Get agent configuration.
    
    Retrieves the current configuration of the agent associated with the specified session.
    """
    config = await service.get_agent_config(session_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return config


@router.patch("/{session_id}/agent", response_model=AgentUpdateResponse)
@version(2)
async def update_agent_config(
    session_id: str,
    update_data: AgentUpdate,
    service: SessionService = Depends(get_session_service)
):
    """
    Update agent configuration.
    
    Updates one or more configuration parameters of the agent associated with the specified session.
    Returns the updated configuration along with details about which changes were applied.
    """
    result = await service.update_agent_config(session_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return result