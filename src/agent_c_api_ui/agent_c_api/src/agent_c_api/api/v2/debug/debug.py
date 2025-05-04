# src/agent_c_api/api/v2/debug/debug.py
import structlog

from fastapi import APIRouter, Depends, HTTPException
from ....core.agent_manager import UItoAgentBridgeManager
from ...dependencies import get_agent_manager
from ..models.debug_models import SessionDebugInfo, AgentDebugInfo
from ..models.response_models import APIResponse, APIStatus

# Configure structured logging
logger = structlog.get_logger()

# Create a router with a debug prefix
router = APIRouter(tags=["Debug"])


@router.get("/sessions/{session_id}", response_model=APIResponse[SessionDebugInfo])
async def get_session_debug_info(session_id: str, agent_manager: UItoAgentBridgeManager = Depends(get_agent_manager)):
    """
    Get comprehensive debug information about a session.
    
    This endpoint provides detailed information about the session state,
    including chat history statistics, memory status, and tool configuration.
    Intended for development and troubleshooting purposes.
    
    Args:
        session_id: The unique identifier for the session
        
    Returns:
        Detailed debug information about the session
    
    Raises:
        404: If the session does not exist
        500: If there's an error retrieving debug information
    """
    try:
        debug_info = await agent_manager.debug_session(session_id)
        return APIResponse(
            status=APIStatus(
                success=True,
                message="Session debug information retrieved successfully"
            ),
            data=debug_info
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error retrieving session debug info", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error retrieving debug information: {str(e)}")


@router.get("/agent/{session_id}", response_model=APIResponse[AgentDebugInfo])
async def get_agent_debug_info(session_id: str, agent_manager: UItoAgentBridgeManager = Depends(get_agent_manager)):
    """
    Get detailed debug information about an agent's state and configuration.
    
    This endpoint provides detailed information about the agent's internal state,
    including configuration parameters, temperature settings, and other runtime properties.
    Intended for development and troubleshooting purposes.
    
    Args:
        session_id: The unique identifier for the session containing the agent
        
    Returns:
        Detailed debug information about the agent's state
    
    Raises:
        404: If the session or agent does not exist
        500: If there's an error retrieving debug information
    """
    try:
        session_data = agent_manager.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        agent = session_data["agent"]

        # Get ReactJSAgent parameters
        agent_bridge_params = {
            "temperature": getattr(agent, "temperature", None),
            "reasoning_effort": getattr(agent, "reasoning_effort", None),
            "extended_thinking": getattr(agent, "extended_thinking", None),
            "budget_tokens": getattr(agent, "budget_tokens", None),
            "max_tokens": getattr(agent, "max_tokens", None),
        }

        # Get internal agent parameters
        internal_agent_params = {}
        if hasattr(agent, "agent") and agent.agent:
            internal_agent = agent.agent
            internal_agent_params = {
                "type": type(internal_agent).__name__,
                "temperature": getattr(internal_agent, "temperature", None),
                "reasoning_effort": getattr(internal_agent, "reasoning_effort", None),
                "budget_tokens": getattr(internal_agent, "budget_tokens", None),
                "max_tokens": getattr(internal_agent, "max_tokens", None),
            }

        debug_info = {
            "status": "success",
            "agent_bridge_params": agent_bridge_params,
            "internal_agent_params": internal_agent_params,
        }

        return APIResponse(
            status=APIStatus(
                success=True,
                message="Agent debug information retrieved successfully"
            ),
            data=debug_info
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving agent debug info", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error retrieving agent debug information: {str(e)}")