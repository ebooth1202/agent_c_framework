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
from agent_c_api.core.voice.models import open_ai_voice_models, heygen_avatar_voice_model, no_voice_model
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

    voices = [no_voice_model, heygen_avatar_voice_model] + open_ai_voice_models
    
    return RealtimeLoginResponse(agent_c_token=login_response.token,
                                 heygen_token=heygen_token,
                                 user=login_response.user,
                                 agents=agents,
                                 avatars=avatar_list,
                                 ui_session_id=MnemonicSlugs.generate_slug(3),
                                 toolsets=tools,
                                 voices=voices)

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
