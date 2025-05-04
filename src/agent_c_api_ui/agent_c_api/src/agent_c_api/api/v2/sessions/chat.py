from typing import List, Optional, AsyncGenerator, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from fastapi.responses import StreamingResponse, JSONResponse
import json
import asyncio
import structlog

from agent_c_api.api.dependencies import get_agent_manager
from agent_c_api.core.agent_manager import UItoAgentBridgeManager
from agent_c_api.core.file_handler import FileHandler

from agent_c_api.api.v2.models.chat_models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatEventUnion
)

from agent_c_api.api.v2.sessions.services import SessionService

router = APIRouter()
logger = structlog.get_logger(__name__)


class ChatService:
    """Service for handling chat operations with sessions"""

    def __init__(self, agent_manager: UItoAgentBridgeManager = Depends(get_agent_manager)):
        self.agent_manager = agent_manager
        self.logger = structlog.get_logger(__name__)

    async def send_message(
        self, 
        session_id: str, 
        message: ChatMessage,
        file_ids: Optional[List[str]] = None
    ) -> AsyncGenerator[ChatEventUnion, None]:
        """Send a message to the agent and stream the response
        
        Args:
            session_id: The session identifier
            message: The message to send
            file_ids: Optional list of file IDs to attach to the message
            
        Yields:
            Stream of chat events from the agent
            
        Raises:
            HTTPException: If the session doesn't exist or other errors occur
        """
        # Verify the session exists
        session_data = self.agent_manager.get_session_data(session_id)
        if not session_data:
            self.logger.error("chat_session_not_found", session_id=session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        # For 'user' messages, extract the text content for processing
        # In the future, we can enhance this to handle multimodal content
        if message.role != "user":
            self.logger.error("invalid_message_role", role=message.role)
            raise HTTPException(status_code=400, detail="Only 'user' role messages are accepted")
        
        # Extract text content from the message (concatenating multiple text blocks if present)
        text_content = ""
        for content_part in message.content:
            if content_part.type == "text" and content_part.text:
                text_content += content_part.text + "\n"
        
        text_content = text_content.strip()
        if not text_content:
            self.logger.error("empty_message_content")
            raise HTTPException(status_code=400, detail="Message must contain text content")
            
        try:
            # Stream the response from the agent manager
            async for token in self.agent_manager.stream_response(
                session_id,
                user_message=text_content,
                file_ids=file_ids
            ):
                # For now, we're returning the raw tokens
                # In a future enhancement, we could parse these into structured events
                # based on the format of the token
                yield token
        except Exception as e:
            self.logger.error("stream_response_error", session_id=session_id, error=str(e))
            raise HTTPException(
                status_code=500, 
                detail=f"Error streaming response: {str(e)}"
            )
    
    async def cancel_interaction(self, session_id: str) -> bool:
        """Cancel an ongoing interaction in a session
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if cancellation was successful, False otherwise
            
        Raises:
            HTTPException: If the session doesn't exist
        """
        # Verify the session exists
        session_data = self.agent_manager.get_session_data(session_id)
        if not session_data:
            self.logger.error("cancel_session_not_found", session_id=session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Attempt to cancel the interaction
        success = self.agent_manager.cancel_interaction(session_id)
        
        self.logger.info(
            "interaction_cancellation", 
            session_id=session_id, 
            success=success
        )
        
        return success


@router.post(
    "/{session_id}/chat", 
    response_model=None,  # Using None as we'll return a streaming response
    summary="Send a chat message to the agent",
    description="Sends a chat message to the agent and receives a streaming response"
)
async def send_chat_message(
    session_id: str = Path(..., description="ID of the session"),
    request: ChatRequest = Body(..., description="Chat message request"),
    chat_service: ChatService = Depends(),
    session_service: SessionService = Depends()
):
    """Send a chat message to the agent and receive the response
    
    Args:
        session_id: ID of the session to send the message to
        request: The chat message request containing the message and streaming preference
        chat_service: Dependency-injected chat service
        session_service: Dependency-injected session service
        
    Returns:
        StreamingResponse if streaming is enabled, otherwise a standard JSON response
    """
    # Verify the session exists
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Extract file IDs from message content if present
    file_ids = []
    for content in request.message.content:
        if content.type in ["file", "image"] and content.file_id:
            file_ids.append(content.file_id)
    
    # If streaming is requested, return a streaming response
    if request.stream:
        async def event_stream():
            try:
                async for token in chat_service.send_message(
                    session_id, 
                    request.message,
                    file_ids if file_ids else None
                ):
                    # Each token is a piece of the response
                    # Ensure newlines for proper streaming
                    if not token.endswith('\n'):
                        token += '\n'
                    yield token
            except Exception as e:
                logger.error("chat_streaming_error", error=str(e))
                yield f"Error: {str(e)}\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    else:
        # For non-streaming responses, we would need to collect the full response
        # This would involve changing send_message to support non-streaming mode
        # For now, we'll just reject non-streaming requests
        raise HTTPException(
            status_code=501, 
            detail="Non-streaming mode is not supported yet"
        )


@router.delete(
    "/{session_id}/chat", 
    response_model=Dict[str, Any],
    summary="Cancel an ongoing chat interaction",
    description="Cancels an ongoing interaction in the specified session"
)
async def cancel_chat_interaction(
    session_id: str = Path(..., description="ID of the session"),
    chat_service: ChatService = Depends(),
    session_service: SessionService = Depends()
):
    """Cancel an ongoing chat interaction
    
    Args:
        session_id: ID of the session with the interaction to cancel
        chat_service: Dependency-injected chat service
        session_service: Dependency-injected session service
        
    Returns:
        JSON response with cancellation status
    """
    # Verify the session exists
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Attempt to cancel the interaction
    success = await chat_service.cancel_interaction(session_id)
    
    if success:
        return {
            "status": "success",
            "message": f"Cancellation signal sent for session: {session_id}"
        }
    else:
        return {
            "status": "error",
            "message": f"Failed to cancel interaction for session: {session_id}"
        }