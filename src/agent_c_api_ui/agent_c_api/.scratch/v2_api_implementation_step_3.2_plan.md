# Agent C API V2 - Implementation Step 3.2: Agent Configuration Management

## Overview

This document outlines the implementation plan for Phase 3, Step 2 of our API v2 development, focusing on Agent Configuration Management. These endpoints will allow clients to retrieve and update agent configuration within a specific session.

## 1. Current State Assessment

Based on analysis of the v1 API and our redesign findings, the current agent configuration management functionality is implemented in:

- `/v1/agent.py` - Contains endpoints for updating agent settings and getting agent configuration
- `/core/agent_manager.py` - Contains the `UItoAgentBridgeManager` class that maintains agent configurations
- `/v1/llm_models/agent_params.py` - Contains parameter models for agent configuration

The v1 API has the following relevant endpoints:

- `get_agent_config`: Retrieves the configuration of an agent in a specific session
- `update_agent_settings`: Updates agent parameters (temperature, reasoning_effort, etc.)

These endpoints provide functionality for managing agent configuration, but they use inconsistent naming patterns and are mixed with other agent-related endpoints.

## 2. Implementation Components

### 2.1 Model Definitions

We'll create the following Pydantic models in `/api/v2/sessions/models.py` (extending what we already implemented in step 3.1):

1. **AgentConfig** - Detailed agent configuration model:
   ```python
   class AgentConfig(BaseModel):
       """Detailed agent configuration information"""
       model_id: str = Field(..., description="ID of the LLM model being used")
       persona_id: str = Field(..., description="ID of the persona being used")
       custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
       temperature: Optional[float] = Field(None, description="Temperature parameter for the model")
       reasoning_effort: Optional[int] = Field(None, description="Reasoning effort parameter (for OpenAI)")
       budget_tokens: Optional[int] = Field(None, description="Budget tokens parameter (for Claude)")
       max_tokens: Optional[int] = Field(None, description="Maximum tokens for model output")
       tools: List[str] = Field(default_factory=list, description="List of enabled tool IDs")
   ```

2. **AgentUpdate** - Model for updating agent configuration:
   ```python
   class AgentUpdate(BaseModel):
       """Model for updating agent configuration"""
       persona_id: Optional[str] = Field(None, description="ID of the persona to use")
       custom_prompt: Optional[str] = Field(None, description="Custom prompt overriding the persona")
       temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Temperature parameter for the model")
       reasoning_effort: Optional[int] = Field(None, ge=0, le=10, description="Reasoning effort parameter (for OpenAI)")
       budget_tokens: Optional[int] = Field(None, ge=0, description="Budget tokens parameter (for Claude)")
       max_tokens: Optional[int] = Field(None, ge=0, description="Maximum tokens for model output")
   ```

3. **AgentUpdateResponse** - Response model for agent updates:
   ```python
   class AgentUpdateResponse(BaseModel):
       """Response for agent configuration updates"""
       agent_config: AgentConfig = Field(..., description="Updated agent configuration")
       changes_applied: Dict[str, Any] = Field(default_factory=dict, description="Changes that were applied")
       changes_skipped: Dict[str, Any] = Field(default_factory=dict, description="Changes that were skipped")
   ```

### 2.2 Service Implementation

We'll extend our `SessionService` class in `/api/v2/sessions/services.py` with methods for agent configuration management:

```python
async def get_agent_config(self, session_id: str) -> Optional[AgentConfig]:
    """Get agent configuration for a session"""
    # Check if session exists
    session = await self.get_session(session_id)
    if not session:
        return None
        
    # Get agent configuration from the agent manager
    agent_config = self.agent_manager.get_agent_config(session_id)
    if not agent_config:
        return None
        
    # Convert to AgentConfig model
    return AgentConfig(
        model_id=agent_config.get("model_name", ""),
        persona_id=agent_config.get("persona_name", "default"),
        custom_prompt=agent_config.get("custom_prompt"),
        temperature=agent_config.get("temperature"),
        reasoning_effort=agent_config.get("reasoning_effort"),
        budget_tokens=agent_config.get("budget_tokens"),
        max_tokens=agent_config.get("max_tokens"),
        tools=agent_config.get("tools", [])
    )

async def update_agent_config(self, session_id: str, update_data: AgentUpdate) -> Optional[AgentUpdateResponse]:
    """Update agent configuration for a session"""
    # Check if session exists
    session = await self.get_session(session_id)
    if not session:
        return None
        
    # Convert AgentUpdate to AgentUpdateParams (v1 model)
    from agent_c_api.api.v1.llm_models.agent_params import AgentUpdateParams
    update_params = AgentUpdateParams(
        ui_session_id=session_id,
        persona_name=update_data.persona_id if update_data.persona_id is not None else None,
        custom_prompt=update_data.custom_prompt,
        temperature=update_data.temperature,
        reasoning_effort=update_data.reasoning_effort,
        budget_tokens=update_data.budget_tokens,
        max_tokens=update_data.max_tokens
    )
    
    # Update agent configuration using agent manager
    update_result = self.agent_manager.update_agent_settings(update_params)
    if not update_result:
        return None
        
    # Get updated agent configuration
    updated_config = await self.get_agent_config(session_id)
    if not updated_config:
        return None
        
    # Return update response
    return AgentUpdateResponse(
        agent_config=updated_config,
        changes_applied=update_result.get("changes_applied", {}),
        changes_skipped=update_result.get("changes_skipped", {})
    )
```

### 2.3 Router Implementation

We'll create a new router in `/api/v2/sessions/agent.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi_versioning import version

from agent_c_api.api.v2.sessions.models import AgentConfig, AgentUpdate, AgentUpdateResponse
from agent_c_api.api.v2.sessions.services import SessionService
from agent_c_api.api.dependencies import get_session_service

router = APIRouter(tags=["agent"])

@router.get("/{session_id}/agent", response_model=AgentConfig)
@version(2)
async def get_agent_config(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Get agent configuration.
    
    Retrieves the current configuration of the agent associated with the specified session.
    """
    config = await service.get_agent_config(session_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return config

@router.patch("/{session_id}/agent", response_model=AgentUpdateResponse)
@version(2)
async def update_agent_config(
    session_id: str,
    update_data: AgentUpdate,
    service: SessionService = Depends(get_session_service)
):
    """
    Update agent configuration.
    
    Updates one or more configuration parameters of the agent associated with the specified session.
    Returns the updated configuration along with details about which changes were applied.
    """
    result = await service.update_agent_config(session_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return result
```

### 2.4 Integration

We'll update the main sessions router in `/api/v2/sessions/__init__.py` to include the agent router:

```python
from fastapi import APIRouter
from .sessions import router as sessions_router
from .agent import router as agent_router

router = APIRouter(prefix="/sessions")
router.include_router(sessions_router)
router.include_router(agent_router)
```

## 3. Test Plan

### 3.1 Unit Tests

We'll create unit tests in `/tests/v2/sessions/test_agent.py`:

1. **Service Tests**
   - Test agent configuration retrieval
   - Test agent configuration updates with various parameters
   - Test handling of missing sessions
   - Test validation of update parameters

2. **Endpoint Tests**
   - Test GET endpoint for retrieving agent configuration
   - Test PATCH endpoint for updating agent configuration
   - Test error responses (404 for non-existent sessions)
   - Test validation errors (e.g., temperature out of range)

### 3.2 Integration Tests

We'll create integration tests that verify the entire flow:

- Test creating a session, then retrieving its agent configuration
- Test updating agent configuration and verifying changes
- Test the interaction between agent config updates and the agent manager

## 4. Implementation Steps

1. **Update Models** (0.5 day)
   - Add AgentConfig, AgentUpdate, and AgentUpdateResponse to sessions/models.py
   - Write tests for model validation

2. **Extend Service Layer** (1 day)
   - Add get_agent_config and update_agent_config methods to SessionService
   - Write tests for service functions

3. **Create Agent Router** (0.5 day)
   - Implement router with GET and PATCH endpoints
   - Connect to service layer

4. **Integration** (0.5 day)
   - Update sessions module to include agent router
   - Test the entire flow

5. **Documentation** (0.5 day)
   - Update API documentation with new endpoints
   - Add examples for each operation

## 5. Dependencies and Required Changes

1. **Get Dependencies**
   - We need to create a `get_session_service` dependency in `/api/dependencies.py` if it doesn't already exist

2. **Integration with Existing Functionality**
   - Ensure proper interaction with the `UItoAgentBridgeManager`
   - Handle agent configuration changes efficiently

## 6. Expected Outcomes

Upon completion of this step, we'll have a fully functional agent configuration API that allows:

1. Retrieving detailed agent configuration for a specific session
2. Updating agent configuration parameters with proper validation
3. Getting detailed information about which updates were applied

These endpoints will follow RESTful patterns with proper resource naming and HTTP methods, improving on the v1 API design.

## 7. Risks and Mitigations

1. **Risk**: Agent manager may not support all update operations cleanly
   **Mitigation**: Add adapter methods in the service layer to handle differences

2. **Risk**: Parameter validation may differ between models and LLM backends
   **Mitigation**: Add robust validation in the AgentUpdate model

3. **Risk**: Updates might require complex transformations
   **Mitigation**: Carefully test the conversion between v2 and v1 models

## 8. Example Requests and Responses

### Get Agent Configuration
```http
GET /api/v2/sessions/sess_12345/agent HTTP/1.1
```

Response:
```json
{
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "custom_prompt": null,
  "temperature": 0.7,
  "reasoning_effort": 5,
  "budget_tokens": null,
  "max_tokens": 2000,
  "tools": ["search", "calculator"]
}
```

### Update Agent Configuration
```http
PATCH /api/v2/sessions/sess_12345/agent HTTP/1.1
Content-Type: application/json

{
  "temperature": 0.8,
  "persona_id": "researcher",
  "reasoning_effort": 7
}
```

Response:
```json
{
  "agent_config": {
    "model_id": "gpt-4",
    "persona_id": "researcher",
    "custom_prompt": null,
    "temperature": 0.8,
    "reasoning_effort": 7,
    "budget_tokens": null,
    "max_tokens": 2000,
    "tools": ["search", "calculator"]
  },
  "changes_applied": {
    "temperature": 0.8,
    "persona_id": "researcher",
    "reasoning_effort": 7
  },
  "changes_skipped": {}
}
```

This detailed plan provides a solid foundation for implementing Phase 3.2: Agent Configuration Management. Once completed, we can move on to implementing the tools management endpoints in Phase 3.3.