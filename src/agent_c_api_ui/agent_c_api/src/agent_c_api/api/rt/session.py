from typing import Optional, Dict, Any, TYPE_CHECKING
from fastapi import APIRouter, HTTPException, Depends, WebSocket, Request

from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.models.client_tool_info import ClientToolInfo
from agent_c.toolsets import Toolset
from agent_c.util import MnemonicSlugs
from agent_c.util.heygen_streaming_avatar_client import HeyGenStreamingClient
from agent_c.util.logging_utils import LoggingManager
from agent_c_api.api.dependencies import get_agent_manager, get_auth_service
from agent_c_api.core.util.jwt import validate_websocket_jwt, validate_request_jwt, create_jwt_token, verify_jwt_token
from agent_c_api.models.auth_models import UserLoginRequest, RealtimeLoginResponse

if TYPE_CHECKING:
    from agent_c_api.core.services.auth_service import AuthService

router = APIRouter()
logger = LoggingManager(__name__).get_logger()



@router.post("/login", response_model=RealtimeLoginResponse)
async def login(login_request: UserLoginRequest, auth_service: "AuthService" = Depends(get_auth_service)) -> RealtimeLoginResponse:
    """
    Authenticate user and return config with token.
    """
    login_response = await auth_service.login(login_request.username, login_request.password)
    
    if not login_response:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get config data
    heygen_client = HeyGenStreamingClient()
    heygen_token = await heygen_client.create_streaming_access_token()
    loader: AgentConfigLoader = AgentConfigLoader()
    agents = loader.client_catalog
    avatar_list = (await heygen_client.list_avatars()).data
    tools = [ClientToolInfo.from_toolset(tool_class) for tool_class in Toolset.tool_registry]
    tools.sort(key=lambda x: x['name'].lower())

    # TODO: Grab the chat session index entries for the user and include them in the response
    
    return RealtimeLoginResponse(agent_c_token=login_response.token,
                                 heygen_token=heygen_token,
                                 user=login_response.user,
                                 agents=agents,
                                 avatars=avatar_list,
                                 ui_session_id=MnemonicSlugs.generate_slug(3),
                                 toolsets=tools)

@router.get("/refresh_token")
async def refresh_token(request: Request):
    """
    Refreshes the JWT token for the user.
    """
    user_info = await validate_request_jwt(request)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")

    heygen_client = HeyGenStreamingClient()
    heygen_token = await heygen_client.create_streaming_access_token()
    new_token = create_jwt_token(user_info['user_id'], user_info.get('permissions', []))
    return {"agent_c_token": new_token, 'heygen_token': heygen_token}


@router.websocket("/ws")
async def initialize_realtime_session(websocket: WebSocket,
                                      token: str,
                                      session_id: Optional[str] = None):
    """
    Creates an agent session with the provided parameters.
    """
    try:
        user_info: Dict[str, Any] = verify_jwt_token(token)
        auth_service: 'AuthService' = websocket.app.state.auth_service
        user = await auth_service.auth_repo.get_user_by_id(user_info['user_id'])
        manager = websocket.app.state.realtime_manager
        ui_session = await manager.create_realtime_session(user, session_id)

        await ui_session.bridge.run(websocket)

    except Exception as e:
        logger.exception(f"Error during session initialization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_avatar_config(request: Request):
    """
    Retrieves the configuration for the avatar session.

    Returns:
        dict: A dictionary containing the avatar session configuration.
    """
    #_ = validate_request_jwt(request)
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


@router.get("/verify_session/{ui_session_id}")
async def verify_session(ui_session_id: str, request: Request):
    """
    Verifies if a session exists and is valid
    """
    user_info = await validate_request_jwt(request)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")

    agent_manager = get_agent_manager(request)
    session_data = agent_manager.get_session_data(ui_session_id)
    if session_data and session_data.user_id != user_info['user_id']:
        session_data = None  # Invalidate if user IDs don't match

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
