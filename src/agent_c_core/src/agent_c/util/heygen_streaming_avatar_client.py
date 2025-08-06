"""
HeyGen Streaming Avatar API Client

This module provides an httpx-based client for interacting with the HeyGen Streaming Avatar API.
"""

from typing import Optional
from datetime import datetime
import httpx

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


class HeyGenStreamingAvatarClient:
    """
    HTTP client for HeyGen Streaming Avatar API.
    
    Provides methods to interact with all HeyGen Streaming Avatar endpoints
    using httpx for HTTP requests and Pydantic models for data validation.
    """
    
    BASE_URL = "https://api.heygen.com"
    
    def __init__(self, api_key: str, timeout: float = 30.0):
        """
        Initialize the HeyGen client.
        
        Args:
            api_key: HeyGen API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
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
    
    async def list_avatars(self) -> ListAvatarsResponse:
        """
        List available streaming avatars.
        
        Returns:
            ListAvatarsResponse containing available avatars
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.get("/v1/streaming/avatar.list")
        response.raise_for_status()
        return ListAvatarsResponse.model_validate(response.json())
    
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
        response = await self._client.post(
            "/v1/streaming.new",
            json=request.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        return NewSessionResponse.model_validate(response.json())
    
    async def start_session(self, request: SessionIdRequest) -> SimpleStatusResponse:
        """
        Start an existing streaming session.
        
        Args:
            request: Session start parameters
            
        Returns:
            SimpleStatusResponse containing status
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post(
            "/v1/streaming.start",
            json=request.model_dump()
        )
        response.raise_for_status()
        return SimpleStatusResponse.model_validate(response.json())
    
    async def send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Send a task to an active session.
        
        Args:
            request: Task parameters including session_id and text
            
        Returns:
            SendTaskResponse containing task response with duration and task_id
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post(
            "/v1/streaming.task",
            json=request.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        return SendTaskResponse.model_validate(response.json())
    
    async def interrupt_task(self, request: SessionIdRequest) -> HeyGenBaseResponse:
        """
        Interrupt a running task in a session.
        
        Args:
            request: Task interruption parameters
            
        Returns:
            HeyGenBaseResponse containing interruption response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post(
            "/v1/streaming.interrupt",
            json=request.model_dump()
        )
        response.raise_for_status()
        return HeyGenBaseResponse.model_validate(response.json())
    
    async def close_session(self, request: SessionIdRequest) -> SimpleStatusResponse:
        """
        Close an active session.
        
        Args:
            request: Session closure parameters
            
        Returns:
            SimpleStatusResponse containing closure response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post(
            "/v1/streaming.stop",
            json=request.model_dump()
        )
        response.raise_for_status()
        return SimpleStatusResponse.model_validate(response.json())
    
    async def keep_alive(self, request: SessionIdRequest) -> HeyGenBaseResponse:
        """
        Reset the idle timeout countdown for an active session.
        
        Args:
            request: Keep alive parameters
            
        Returns:
            HeyGenBaseResponse containing keep alive response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post(
            "/v1/streaming.keep_alive",
            json=request.model_dump()
        )
        response.raise_for_status()
        return HeyGenBaseResponse.model_validate(response.json())
    
    async def create_session_token(self) -> CreateSessionTokenResponse:
        """
        Create a session token.
        
        Returns:
            CreateSessionTokenResponse containing the token
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.post("/v1/streaming.create_token", json={})
        response.raise_for_status()
        return CreateSessionTokenResponse.model_validate(response.json())
    
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
        params = {
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