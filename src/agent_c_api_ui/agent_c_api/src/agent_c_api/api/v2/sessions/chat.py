from typing import List, Optional, AsyncGenerator, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi_versioning import version
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

router = APIRouter(tags=["sessions"])
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
    ) -> AsyncGenerator[str, None]:
        """Send a message to the agent and stream the response
        
        This method sends a message to an agent in a specific session and returns a stream
        of JSON-encoded events representing the agent's response. The stream includes
        incremental text updates, tool calls, and completion status updates.
        
        Args:
            session_id: The unique identifier for the session
            message: The message to send, including content parts (text, files, etc.)
            file_ids: Optional list of file IDs to attach to the message (can be extracted from message content)
            
        Yields:
            Stream of JSON-encoded chat events from the agent, including:
            - text_delta: Incremental text updates from the assistant
            - tool_call: Tool invocation events when tools are used
            - thought_delta: Thinking process updates (when available)
            - completion: Final completion status when the response is complete
            
        Raises:
            HTTPException(404): If the session doesn't exist
            HTTPException(400): If the message has invalid format or empty content
            HTTPException(500): If there's an error processing the message
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
            # The events are already JSON-encoded strings from the agent,
            # so we just pass them through directly
            async for event_json in self.agent_manager.stream_response(
                session_id,
                user_message=text_content,
                file_ids=file_ids
            ):
                # Just yield the JSON event string directly
                yield event_json
        except Exception as e:
            self.logger.error("stream_response_error", session_id=session_id, error=str(e))
            raise HTTPException(
                status_code=500, 
                detail=f"Error streaming response: {str(e)}"
            )
    
    async def cancel_interaction(self, session_id: str) -> bool:
        """Cancel an ongoing interaction in a session
        
        This method sends a cancellation signal to an ongoing interaction in the specified
        session. Cancellation is best-effort; there's no guarantee that the agent will
        stop immediately, but it will attempt to halt processing as soon as possible.
        
        Args:
            session_id: The unique identifier for the session containing the interaction to cancel
            
        Returns:
            True if cancellation signal was successfully sent, False if cancellation failed
            or there was no active interaction to cancel
            
        Raises:
            HTTPException(404): If the session doesn't exist
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
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the agent",
    description="Sends a chat message to the agent and receives a streaming response of events",
    responses={
        200: {
            "description": "Successful response with streaming events",
            "content": {
                "text/event-stream": {
                    "example": "\n".join([
                        '{"type":"text_delta","content":"Hello, I\'m Agent C."}',
                        '{"type":"text_delta","content":" How can I help you today?"}',
                        '{"type":"completion","id":"comp_123","status":"complete"}'
                    ])
                }
            }
        },
        400: {
            "description": "Bad request - invalid message format",
            "content": {
                "application/json": {
                    "example": {"detail": "Message must contain text content"}
                }
            }
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Session 550e8400-e29b-41d4-a716-446655440000 not found"}
                }
            }
        },
        500: {
            "description": "Server error processing the message",
            "content": {
                "application/json": {
                    "example": {"detail": "Error streaming response: Agent processing failed"}
                }
            }
        },
        501: {
            "description": "Non-streaming mode not supported",
            "content": {
                "application/json": {
                    "example": {"detail": "Non-streaming mode is not supported yet"}
                }
            }
        }
    }
)
@version(2)
async def send_chat_message(
    session_id: UUID = Path(..., description="UUID of the session to send the message to"),
    request: ChatRequest = Body(..., description="Chat message request containing the message and streaming preference"),
    chat_service: ChatService = Depends(),
    session_service: SessionService = Depends()
):
    """Send a chat message to the agent and receive the response
    
    This endpoint allows sending a message to an agent in a specific session and receiving
    the agent's response. By default, the response is streamed as Server-Sent Events (SSE),
    which enables real-time updates as the agent generates its response.
    
    The message can contain text content, file attachments, or both. File attachments must
    have been previously uploaded using the file upload endpoint.
    
    Args:
        session_id: UUID of the session to send the message to
        request: The chat message request containing the message and streaming preference
        chat_service: Dependency-injected chat service
        session_service: Dependency-injected session service
        
    Returns:
        StreamingResponse: A stream of SSE events representing the agent's response
        
    Raises:
        HTTPException(404): If the session doesn't exist
        HTTPException(400): If the message has invalid format or empty content
        HTTPException(500): If there's an error processing the message
        HTTPException(501): If non-streaming mode is requested (currently unsupported)
        
    Example:
        ```python
        import requests
        import json
        import sseclient
        
        # Prepare the message
        message = {
            "message": {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": "What's the capital of France?"
                }]
            },
            "stream": True
        }
        
        # Send the message and get streaming response
        response = requests.post(
            "https://api.example.com/api/v2/sessions/550e8400-e29b-41d4-a716-446655440000/chat",
            json=message,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        # Process the streaming response
        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            if data.get("type") == "text_delta":
                print(data.get("content"), end="")
        ```
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
                async for event_json in chat_service.send_message(
                    session_id, 
                    request.message,
                    file_ids if file_ids else None
                ):
                    # The events from agent_manager are already JSON strings
                    # Just make sure they end with a newline for SSE
                    if not event_json.endswith('\n'):
                        event_json += '\n'
                    yield event_json
            except Exception as e:
                logger.error("chat_streaming_error", error=str(e))
                error_event = {
                    "type": "error",
                    "content": f"Error: {str(e)}"
                }
                yield json.dumps(error_event) + '\n'
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
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
    status_code=status.HTTP_200_OK,
    summary="Cancel an ongoing chat interaction",
    description="Cancels an ongoing interaction in the specified session",
    responses={
        200: {
            "description": "Successful cancellation",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Cancellation signal sent for session: 550e8400-e29b-41d4-a716-446655440000"
                    }
                }
            }
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Session 550e8400-e29b-41d4-a716-446655440000 not found"}
                }
            }
        },
        500: {
            "description": "Failed to cancel interaction",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Failed to cancel interaction for session: 550e8400-e29b-41d4-a716-446655440000"
                    }
                }
            }
        }
    }
)
@version(2)
async def cancel_chat_interaction(
    session_id: UUID = Path(..., description="UUID of the session with the interaction to cancel"),
    chat_service: ChatService = Depends(),
    session_service: SessionService = Depends()
):
    """Cancel an ongoing chat interaction
    
    This endpoint sends a cancellation signal to stop an ongoing interaction with an agent.
    It's useful when you need to interrupt a long-running interaction, such as when the
    user wants to ask a different question or the agent is stuck in a loop.
    
    Cancellation is best-effort; there's no guarantee that the agent will stop immediately,
    but it will attempt to halt processing as soon as possible.
    
    Args:
        session_id: UUID of the session with the interaction to cancel
        chat_service: Dependency-injected chat service
        session_service: Dependency-injected session service
        
    Returns:
        Dict[str, Any]: JSON response with cancellation status (success/error) and message
        
    Raises:
        HTTPException(404): If the session doesn't exist
        
    Example:
        ```python
        import requests
        
        # Send cancellation request
        response = requests.delete(
            "https://api.example.com/api/v2/sessions/550e8400-e29b-41d4-a716-446655440000/chat",
        )
        
        result = response.json()
        print(f"Cancellation {result['status']}: {result['message']}")
        ```
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