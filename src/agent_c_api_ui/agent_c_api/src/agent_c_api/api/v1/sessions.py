from fastapi import APIRouter, HTTPException, Depends
import logging
from agent_c_api.api.dependencies import get_agent_manager, get_dynamic_params

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/initialize")
async def initialize_session(
        model_name: str = "gpt-4o",
        backend: str = "openai",
        persona_name: str = "",
        dynamic_params = Depends(get_dynamic_params),
        agent_manager=Depends(get_agent_manager)
):
    """
    Creates a fresh session with the provided parameters.
    """
    try:
        # Create a new session with both model and backend parameters
        logging.debug(f"Creating new session with model: {model_name}, backend: {backend}")

        # Conditionally pass model param
        model_params = dynamic_params.dict()

        new_session_id = await agent_manager.create_session(
            llm_model=model_name,
            backend=backend,
            persona_name=persona_name,
            **model_params
        )

        logger.debug(f"Current sessions in memory: {list(agent_manager.sessions.keys())}")
        logger.debug(
            f"User Session {new_session_id} with session details: {agent_manager.get_session_data(new_session_id)}")
        return {"session_id": new_session_id,
                "agent_c_session_id": agent_manager.get_session_data(new_session_id).get('agent_c_session_id',
                                                                                         "Unknown")}

    except Exception as e:
        logger.error(f"Error during session initialization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify_session/{session_id}")
async def verify_session(session_id: str, agent_manager=Depends(get_agent_manager)):
    """
    Verifies if a session exists and is valid
    """
    session_data = agent_manager.get_session_data(session_id)
    return {"valid": session_data is not None}


@router.delete("/sessions")
async def delete_all_sessions(agent_manager=Depends(get_agent_manager)):
    """
    Delete all active sessions and cleanup their resources.

    Returns:
        dict: Status message with number of sessions deleted

    Raises:
        HTTPException: If there's an error during session cleanup
    """
    try:
        # Get count of sessions before deletion
        session_count = len(agent_manager.sessions)

        # Create list of session IDs to avoid modifying dict during iteration
        session_ids = list(agent_manager.sessions.keys())

        # Clean up each session
        for session_id in session_ids:
            await agent_manager.cleanup_session(session_id)

        logger.debug(
            f"Deleted {session_count} sessions. Hanging sessions from deletion: {list(agent_manager.sessions.keys())}")

        return {
            "status": "success",
            "message": f"Successfully deleted {session_count} sessions",
            "deleted_count": session_count
        }

    except Exception as e:
        logger.error(f"Error deleting sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete sessions: {str(e)}"
        )
