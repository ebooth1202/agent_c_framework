from fastapi import APIRouter, HTTPException, Form, Depends
import logging
from fastapi.responses import StreamingResponse

from agent_c_api.api.dependencies import get_agent_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat_endpoint(
        session_id: str = Form(...),
        message: str = Form(...),
        custom_prompt: str = Form(""),
        agent_manager=Depends(get_agent_manager)
):
    """
    Endpoint for sending a message and getting a streaming response from the agent.
    We use SSE-like streaming via StreamingResponse.
    """
    logger.info(f"Received chat request for session: {session_id}")
    session_data = agent_manager.get_session_data(session_id)
    # logger.debug(f"Available sessions: {list(agent_manager.sessions.keys())}")

    if not session_data:
        logger.error(f"No session found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_stream():
        """Inner generator for streaming response chunks"""
        # logger.debug(f"Starting event stream for session: {session_id}")
        try:
            async for token in agent_manager.stream_response(
                    session_id,
                    user_message=message,
                    custom_prompt=custom_prompt,
            ):
                # Each token is a piece of the assistant's reply
                yield token
        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            yield f"Error: {str(e)}"

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
