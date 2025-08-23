from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, WebSocket, Request
from sqlalchemy.ext.asyncio import AsyncSession

from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.util.heygen_streaming_avatar_client import HeyGenStreamingClient
from agent_c.util.logging_utils import LoggingManager
from agent_c_api.api.dependencies import get_agent_manager
from agent_c_api.core.util.jwt import validate_websocket_jwt, validate_request_jwt, create_jwt_token
from agent_c_api.config.database import get_db_session

from agent_c_api.models.auth_models import UserLoginRequest, AvatarLoginResponse

router = APIRouter()
logger = LoggingManager(__name__).get_logger()



@router.post("/login", response_model=AvatarLoginResponse)
async def login(login_request: UserLoginRequest, db_session: AsyncSession = Depends(get_db_session)) -> AvatarLoginResponse:
    """
    Authenticate user and return config with token.
    """
    from agent_c_api.core.services.auth_service import AuthService
    auth_service = AuthService(db_session)
    login_response = await auth_service.login(login_request.username, login_request.password)
    
    if not login_response:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get config data
    heygen_client = HeyGenStreamingClient()
    heygen_token = await heygen_client.create_streaming_access_token()
    loader: AgentConfigLoader = AgentConfigLoader()
    agents = loader.client_catalog
    avatar_list = (await heygen_client.list_avatars()).data
    
    return AvatarLoginResponse(
        agent_c_token=login_response.token,
        heygen_token=heygen_token,
        user=login_response.user,
        agents=agents,
        avatars=avatar_list
    )


@router.get("/config")
async def get_avatar_config():
    """
    Retrieves the configuration for the avatar session.

    Returns:
        dict: A dictionary containing the avatar session configuration.
    """
    try:
        heygen_client = HeyGenStreamingClient()
        loader: AgentConfigLoader = AgentConfigLoader()
        agents = loader.client_catalog
        avatar_list = (await heygen_client.list_avatars()).data
        return {'agents': agents, "avatars": avatar_list}

    except Exception as e:
        logger.error(f"Error retrieving avatar config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve avatar config: {str(e)}"
        )


@router.websocket("/ws")
async def initialize_avatar_session(websocket: WebSocket,
                                    session_id: Optional[str] = None):
    """
    Creates an agent session with the provided parameters.
    """
    try:
        user_info: Dict[str, Any] = await validate_websocket_jwt(websocket)
        agent_manager = websocket.app.state.agent_manager
        avatar_bridge = await agent_manager.create_avatar_session(user_info['user_id'], session_id)

        await avatar_bridge.run(websocket)

    except Exception as e:
        logger.exception(f"Error during session initialization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify_session/{ui_session_id}")
async def verify_session(ui_session_id: str, request: Request):
    """
    Verifies if a session exists and is valid
    """
    agent_manager = get_agent_manager(request)
    session_data = agent_manager.get_session_data(ui_session_id)
    return {"valid": session_data is not None}

@router.get("/sessions")
async def get_sessions(request: Request):
    """
    Retrieves all available sessions.

    Returns:
        dict: A dictionary containing session IDs and their details

    Raises:
        HTTPException: If there's an error retrieving sessions
    """
    try:
        agent_manager = get_agent_manager(request)
        sessions = agent_manager.chat_session_manager.session_id_list
        return {"session_ids": sessions}

    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )
