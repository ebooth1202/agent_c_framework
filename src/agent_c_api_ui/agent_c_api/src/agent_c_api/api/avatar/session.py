from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket

from agent_c.util.logging_utils import LoggingManager
from agent_c_api.core.agent_manager import UItoAgentBridgeManager
from agent_c_api.api.dependencies import get_agent_manager
from agent_c_api.core.util.jwt import validate_websocket_jwt

router = APIRouter()
logger = LoggingManager(__name__).get_logger()





@router.websocket("/ws")
async def initialize_avatar_session(websocket: WebSocket,
                                    session_id: Optional[str] = None,
                                    agent_manager=Depends(get_agent_manager)):
    """
    Creates an agent session with the provided parameters.
    """
    try:
        user_info = await validate_websocket_jwt(websocket)
        new_session_id = await agent_manager.create_avtar_session(websocket, session_id)
        logger.info(f"Initialized user Session {new_session_id}")

        return {"ui_session_id": new_session_id,
                "agent_c_session_id": new_session_id}

    except Exception as e:
        logger.error(f"Error during session initialization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify_session/{ui_session_id}")
async def verify_session(ui_session_id: str, agent_manager=Depends(get_agent_manager)):
    """
    Verifies if a session exists and is valid
    """
    session_data = agent_manager.get_session_data(ui_session_id)
    return {"valid": session_data is not None}

@router.get("/sessions")
async def get_sessions(agent_manager=Depends(get_agent_manager)):
    """
    Retrieves all available sessions.

    Returns:
        dict: A dictionary containing session IDs and their details

    Raises:
        HTTPException: If there's an error retrieving sessions
    """
    try:
        mgr: UItoAgentBridgeManager = agent_manager
        sessions = mgr.chat_session_manager.session_id_list
        return {"session_ids": sessions}

    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )
