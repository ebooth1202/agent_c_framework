# Dr Research Personas UI Issue - Fix Summary

## Problem Identified

The issue preventing Dr Research from appearing in the UI was in the **v2 Config Service** (`/src/agent_c_api_ui/agent_c_api/src/agent_c_api/api/v2/config/services.py`).

### Root Cause
The `ConfigService` class was missing two critical methods that the v2 config router was trying to call:
1. `get_personas()` - Called by `/api/v2/config/personas` endpoint
2. `get_persona(persona_id)` - Called by `/api/v2/config/personas/{persona_id}` endpoint

This caused the personas endpoints to fail with AttributeError when trying to access these missing methods.

### Additional Issues Found
1. The `get_system_config()` method was calling the missing `get_personas()` method
2. There was a type mismatch - the system config expected `PersonaInfo` objects but the service was returning `AgentConfiguration` objects

## Solution Implemented

### 1. Added Missing Methods
Added the following methods to `ConfigService`:

```python
@cache(expire=300)  # Cache for 5 minutes
async def get_personas(self) -> AgentConfigsResponse:
    """
    Get available personas (agents with 'domo' category) using the existing file-based mechanism
    """
    # Filter agents that have 'domo' in their category (similar to v1 personas endpoint)
    domo_agents = []
    for agent_config in self.agent_config_loader.catalog.values():
        if "domo" in agent_config.category:
            domo_agents.append(agent_config)
    
    return AgentConfigsResponse(agents=domo_agents)

@cache(expire=300)  # Cache for 5 minutes
async def get_persona(self, persona_id: str) -> Optional[PersonaInfo]:
    """
    Get a specific persona by ID, converted to PersonaInfo format
    """
    if persona_id not in self.agent_config_loader.catalog:
        return None
    
    agent_config = self.agent_config_loader.catalog[persona_id]
    
    # Only return if this agent has 'domo' in category (is a persona)
    if "domo" not in agent_config.category:
        return None
    
    # Convert AgentConfiguration to PersonaInfo
    return PersonaInfo(
        id=agent_config.key,
        name=agent_config.name,
        description=agent_config.agent_description,
        file_path=f"{agent_config.key}.yaml",
        content=agent_config.persona[:1000] if agent_config.persona else None  # Truncate for display
    )
```

### 2. Fixed get_system_config Method
Updated the method to properly convert `AgentConfiguration` objects to `PersonaInfo` objects:

```python
@cache(expire=300)  # Cache for 5 minutes
async def get_system_config(self) -> SystemConfigResponse:
    """
    Get combined system configuration
    """
    models_response = await self.get_models()
    personas_response = await self.get_personas()
    tools_response = await self.get_tools()
    
    # Convert AgentConfiguration objects to PersonaInfo objects
    persona_infos = []
    for agent_config in personas_response.agents:
        persona_info = PersonaInfo(
            id=agent_config.key,
            name=agent_config.name,
            description=agent_config.agent_description,
            file_path=f"{agent_config.key}.yaml",
            content=agent_config.persona[:1000] if agent_config.persona else None  # Truncate for display
        )
        persona_infos.append(persona_info)
    
    return SystemConfigResponse(
        models=models_response.models,
        personas=persona_infos,
        tools=tools_response.tools,
        tool_categories=tools_response.categories,
        essential_tools=tools_response.essential_tools
    )
```

### 3. Added Cache Clearing Endpoint
Added a new endpoint to help with cache-related issues:

```python
@router.post("/cache/clear", 
           response_model=APIResponse[dict],
           summary="Clear Configuration Cache",
           description="Clears the configuration cache to force reload of agents, models, and tools.")
async def clear_config_cache():
    """Clear the configuration cache to force reload of agents, models, and tools."""
    try:
        await FastAPICache.clear()
        return APIResponse(
            status=APIStatus(
                success=True,
                message="Configuration cache cleared successfully"
            ),
            data={"cache_cleared": True}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to clear configuration cache",
                "error_code": "CACHE_CLEAR_ERROR",
                "message": str(e)
            }
        )
```

## Verification

### Dr Research Agent Configurations
Both Dr Research agents are properly configured with "domo" in their category:

1. **dr_research** (key: "dr_research")
   - Name: "Dr Research - Medical Research Advisor"
   - Category: ["domo"]
   - ✅ Should appear in personas list

2. **dr_research_no_med** (key: "dr_research_no_med")
   - Name: "Dr Research - No Medical Tools"
   - Category: ["domo"]
   - ✅ Should appear in personas list

## Next Steps

1. **Restart the API service** to load the fixed code
2. **Clear the cache** using the new endpoint: `POST /api/v2/config/cache/clear`
3. **Test the personas endpoint**: `GET /api/v2/config/personas`
4. **Check the UI** to see if Dr Research now appears in the agent selection

## Cache Considerations

The configuration service uses 5-minute caching (`@cache(expire=300)`). If changes don't appear immediately:
1. Wait up to 5 minutes for cache expiration, OR
2. Use the new cache clearing endpoint, OR
3. Restart the API service

## Files Modified

1. `/src/agent_c_api_ui/agent_c_api/src/agent_c_api/api/v2/config/services.py` - Added missing methods and fixed type conversions
2. `/src/agent_c_api_ui/agent_c_api/src/agent_c_api/api/v2/config/router.py` - Added cache clearing endpoint

## Test Script

Created `/project/.scratch/test_personas_fix.py` to verify the fix works correctly without needing to run the full API server.