from fastapi import APIRouter, Depends, HTTPException, Path, Body
from fastapi_versioning import version
from uuid import UUID

from agent_c_api.api.v2.models.session_models import AgentConfig, AgentUpdate, AgentUpdateResponse
from agent_c_api.api.v2.sessions.services import SessionService, get_session_service



router = APIRouter(
    tags=["agent"],
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid agent parameter"
                    }
                }
            }
        },
        404: {
            "description": "Session Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session 550e8400-e29b-41d4-a716-446655440000 not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "temperature"],
                                "msg": "ensure this value is less than or equal to 1.0",
                                "type": "value_error.number.not_le"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to update agent configuration"
                    }
                }
            }
        }
    }
)


@router.get("/{session_id}/agent", 
         response_model=AgentConfig,
         summary="Get agent configuration",
         description="Retrieves the current configuration of the agent associated with the specified session")
@version(2)
async def get_agent_config(
    session_id: UUID = Path(..., description="Unique identifier of the session"),
    service: SessionService = Depends(get_session_service)
):
    """
    Get agent configuration.
    
    Retrieves the complete configuration of the AI agent associated with the specified session.
    This includes the model, persona, temperature, and other parameters that control the agent's behavior.
    
    Args:
        session_id: UUID of the session whose agent configuration to retrieve
        service: Session service dependency injection
        
    Returns:
        AgentConfig: The complete agent configuration
        
    Raises:
        HTTPException: 404 if the session doesn't exist
        
    Example:
        ```python
        import requests
        from uuid import UUID
        
        session_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        
        response = requests.get(
            f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}/agent"
        )
        
        if response.status_code == 200:
            agent_config = response.json()
            print(f"Agent is using {agent_config['model_id']} with {agent_config['persona_id']} persona")
            print(f"Temperature: {agent_config['temperature']}")
            print(f"Tools enabled: {', '.join(agent_config['tools'])}")
        ```
    """
    config = await service.get_agent_config(str(session_id))
    if not config:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return config


@router.patch("/{session_id}/agent", 
           response_model=AgentUpdateResponse,
           summary="Update agent configuration",
           description="Updates one or more configuration parameters of the agent associated with the specified session")
@version(2)
async def update_agent_config(
    session_id: UUID = Path(..., description="Unique identifier of the session"),
    update_data: AgentUpdate = Body(..., description="Agent parameters to update"),
    service: SessionService = Depends(get_session_service)
):
    """
    Update agent configuration.
    
    Updates one or more configuration parameters of the agent associated with the specified session.
    Only the parameters included in the request body will be updated; others will remain unchanged.
    Returns the updated configuration along with details about which changes were applied.
    
    Args:
        session_id: UUID of the session whose agent configuration to update
        update_data: Agent parameters to update, with null/None values ignored
        service: Session service dependency injection
        
    Returns:
        AgentUpdateResponse: The updated agent configuration with change details
        
    Raises:
        HTTPException: 404 if the session doesn't exist
        HTTPException: 422 if validation fails for update parameters
        
    Example:
        ```python
        import requests
        from uuid import UUID
        
        session_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        
        # Update the agent's persona and temperature
        update_data = {
            "persona_id": "researcher",
            "temperature": 0.8
        }
        
        response = requests.patch(
            f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}/agent",
            json=update_data
        )
        
        if response.status_code == 200:
            result = response.json()
            config = result["agent_config"]
            changes = result["changes_applied"]
            
            print(f"Updated to {config['persona_id']} persona")
            print("Changes applied:", changes)
        ```
    """
    result = await service.update_agent_config(str(session_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return result