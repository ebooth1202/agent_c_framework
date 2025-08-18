"""
HeyGen Streaming Avatar API Client

This module provides an httpx-based client for interacting with the HeyGen Streaming Avatar API.
"""
import os
import httpx
import json

from typing import Optional, Dict, Any


from agent_c.models.heygen import (
    # Request models
    NewSessionRequest,
    SendTaskRequest,
    SessionIdRequest,
    
    # Response models
    ListAvatarsResponse,
    NewSessionResponse,
    ListActiveSessionsResponse,
    ListHistoricalSessionsResponse,
    SendTaskResponse,
    CreateSessionTokenResponse,
    HeyGenBaseResponse,
    SimpleStatusResponse,
)
from agent_c.util.logging_utils import LoggingManager


class HeyGenStreamingAvatarClient:
    """
    HTTP client for HeyGen Streaming Avatar API.
    
    Provides methods to interact with all HeyGen Streaming Avatar endpoints
    using httpx for HTTP requests and Pydantic models for data validation.
    """
    
    BASE_URL = "https://api.heygen.com"
    
    def __init__(self,  timeout: float = 30.0, api_key: Optional[str] = None):
        """
        Initialize the HeyGen client.
        
        Args:
            api_key: HeyGen API key for authentication
            timeout: Request timeout in seconds
        """
        self.logger = LoggingManager(__name__).get_logger()
        self.api_key = api_key if api_key else os.environ.get("HEYGEN_API_KEY")
        self.timeout = timeout
        self._client = httpx.AsyncClient( base_url=self.BASE_URL, timeout=timeout,
                                          headers={"x-api-key": api_key, "Content-Type": "application/json" })

    @staticmethod
    def _locate_config_path() -> str:
        """
        Locate configuration path by walking up directory tree.

        Returns:
            Path to agent_c_config directory

        Raises:
            FileNotFoundError: If configuration folder cannot be found
        """
        current_dir = os.getcwd()
        while True:
            config_dir = os.path.join(current_dir, "agent_c_config")
            if os.path.exists(config_dir):
                return config_dir

            parent_dir = os.path.dirname(current_dir)
            if current_dir == parent_dir:  # Reached root directory
                break
            current_dir = parent_dir

        raise FileNotFoundError(
            "Configuration folder not found. Please ensure you are in the correct directory or set AGENT_C_CONFIG_PATH."
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def fetch_avatars(self) -> ListAvatarsResponse:
        """
        Fetch avatars from HeyGen API and cache the results.
        
        This method makes the actual API call to HeyGen, deduplicates the results,
        and saves them to a JSON cache file in the config directory.
        
        Returns:
            ListAvatarsResponse containing unique avatars
            
        Raises:
            httpx.HTTPError: If the request fails
            FileNotFoundError: If config directory cannot be found
        """
        response = await self._client.get("/v1/streaming/avatar.list")
        response.raise_for_status()
        
        raw_response = response.json()
        
        # Deduplicate avatars by avatar_id, keeping the most recent (highest created_at)
        avatars_by_id = {}
        for avatar_data in raw_response["data"]:
            avatar_id = avatar_data["avatar_id"]
            if avatar_id not in avatars_by_id or avatar_data["created_at"] > avatars_by_id[avatar_id]["created_at"]:
                avatars_by_id[avatar_id] = avatar_data
        
        # Reconstruct response with deduplicated avatars
        deduplicated_response = {
            "code": raw_response["code"],
            "message": raw_response["message"],
            "data": list(avatars_by_id.values())
        }
        
        # Cache the results
        try:
            config_path = self._locate_config_path()
            cache_file = os.path.join(config_path, "avatars_cache.json")
            with open(cache_file, 'w') as f:
                json.dump(deduplicated_response, f, indent=2)
        except Exception as e:
            # Log the error but don't fail the request
            # In a production system, you'd want proper logging here
            self.logger.exception("Failed to cache avatars", exc_info=e)
        
        return ListAvatarsResponse.model_validate(deduplicated_response)
    
    async def list_avatars(self) -> ListAvatarsResponse:
        """
        List available streaming avatars.
        
        This method first checks for cached avatar data in the config directory.
        If cached data exists, it loads and returns that. Otherwise, it calls
        fetch_avatars() to get fresh data from the API.
        
        Note: HeyGen's API returns duplicate avatars (different revisions with same avatar_id).
        The fetch method deduplicates by avatar_id, keeping the most recent version.
        
        Returns:
            ListAvatarsResponse containing unique avatars
            
        Raises:
            httpx.HTTPError: If the request fails and no cache is available
        """

        config_path = self._locate_config_path()
        cache_file = os.path.join(config_path, "avatars_cache.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                return ListAvatarsResponse.model_validate(cached_data)
            except Exception:
                self.logger.exception("Failed to load cached avatars", exc_info=True)

        # No cache available or cache loading failed, fetch from API
        return await self.fetch_avatars()
    
    async def create_new_session(self, request: NewSessionRequest) -> NewSessionResponse:
        """
        Create a new streaming avatar session.
        
        Args:
            request: Session creation parameters
            
        Returns:
            NewSessionResponse containing session details
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post("/v1/streaming.new",json=request.model_dump(exclude_none=True))
        response.raise_for_status()
        return NewSessionResponse.model_validate(response.json())
    
    async def start_session(self, session_id: str ) -> SimpleStatusResponse:
        """
        Start an existing streaming session.
        
        Args:
            session_id: The session to start
            
        Returns:
            SimpleStatusResponse containing status
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        request = SessionIdRequest(session_id=session_id)
        response = await self._client.post("/v1/streaming.start", json=request.model_dump() )
        response.raise_for_status()
        return SimpleStatusResponse.model_validate(response.json())
    
    async def send_task(self, session_id: str, text: str, task_mode: str = "async",
                        task_type: str = "repeat") -> SendTaskResponse:
        """
        Send a task to an active session.
        
        Args:
            session_id : The session ID to send the task to
            text: The text input for the task
            task_mode: The mode of the task, either "sync" or "async" (default: "async")
            task_type: The type of task, e.g., "repeat"
            
        Returns:
            SendTaskResponse containing task response with duration and task_id
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        request = SendTaskRequest(session_id=session_id, text=text, task_mode=task_mode, task_type=task_type)
        response = await self._client.post("/v1/streaming.task", json=request.model_dump(exclude_none=True))
        response.raise_for_status()
        return SendTaskResponse.model_validate(response.json())
    
    async def interrupt_task(self, session_id: str) -> HeyGenBaseResponse:
        """
        Interrupt a running task in a session.
        
        Args:
            session_id: The session ID to interrupt
            
        Returns:
            HeyGenBaseResponse containing interruption response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        request = SessionIdRequest(session_id=session_id)
        response = await self._client.post("/v1/streaming.interrupt", json=request.model_dump())
        response.raise_for_status()
        return HeyGenBaseResponse.model_validate(response.json())
    
    async def close_session(self, session_id: str) -> SimpleStatusResponse:
        """
        Close an active session.
        
        Args:
            session_id: The session ID to close
            
        Returns:
            SimpleStatusResponse containing closure response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        request =  SessionIdRequest(session_id=session_id)
        response = await self._client.post("/v1/streaming.stop", json=request.model_dump())
        response.raise_for_status()
        return SimpleStatusResponse.model_validate(response.json())
    
    async def keep_alive(self, session_id: str) -> HeyGenBaseResponse:
        """
        Reset the idle timeout countdown for an active session.
        
        Args:
            session_id: The session ID to keep alive
            
        Returns:
            HeyGenBaseResponse containing keep alive response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        request = SessionIdRequest(session_id=session_id)
        response = await self._client.post("/v1/streaming.keep_alive", json=request.model_dump())
        response.raise_for_status()
        return HeyGenBaseResponse.model_validate(response.json())
    
    async def create_session_token(self) -> str:
        """
        Create a session token.
        
        Returns:
            CreateSessionTokenResponse containing the token
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post("/v1/streaming.create_token", json={})
        response.raise_for_status()
        resp_model =  CreateSessionTokenResponse.model_validate(response.json())
        if resp_model.error:
            raise httpx.HTTPError(f"Error creating session token: {resp_model.error}")
        return resp_model.data.token
    
    async def list_active_sessions(self) -> ListActiveSessionsResponse:
        """
        List currently active sessions.
        
        Returns:
            ListActiveSessionsResponse containing active sessions
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.get("/v1/streaming.list")
        response.raise_for_status()
        return ListActiveSessionsResponse.model_validate(response.json())
    
    async def list_historical_sessions(
        self, 
        page: int = 1, 
        page_size: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        token: Optional[str] = None
    ) -> ListHistoricalSessionsResponse:
        """
        List historical sessions with pagination and filtering support.
        
        Args:
            page: Page number (default: 1)
            page_size: Number of items per page (default: 10)
            date_from: Start date in YYYY-MM-DDTHH:MM:ssZ format (optional)
            date_to: End date in YYYY-MM-DDTHH:MM:ssZ format (optional)
            status: Session status filter (optional)
            token: Next page token (optional)
            
        Returns:
            ListHistoricalSessionsResponse containing historical sessions
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        params: Dict[str, Any] = {
            "page": page,
            "page_size": page_size
        }
        
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if status:
            params["status"] = status
        if token:
            params["token"] = token
            
        response = await self._client.get("/v2/streaming.list", params=params)
        response.raise_for_status()
        return ListHistoricalSessionsResponse.model_validate(response.json())