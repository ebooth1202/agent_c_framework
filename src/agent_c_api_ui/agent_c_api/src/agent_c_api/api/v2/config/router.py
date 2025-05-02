from fastapi import APIRouter, HTTPException, Depends
from fastapi_versioning import version

from .services import ConfigService
from .models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

# Create router with prefix and tags
router = APIRouter(tags=["configuration"])

# Dependency for getting the config service
def get_config_service():
    return ConfigService()

# Models endpoints
@router.get("/models", response_model=ModelsResponse)
@version(2)
async def list_models(
    service: ConfigService = Depends(get_config_service)
):
    """
    List all available LLM models that can be used with agents.
    
    Returns model details including provider, capabilities, and parameters.
    """
    return await service.get_models()

@router.get("/models/{model_id}", response_model=ModelInfo)
@version(2)
async def get_model(
    model_id: str,
    service: ConfigService = Depends(get_config_service)
):
    """
    Get detailed information about a specific model.
    
    Returns the model's configuration details or 404 if not found.
    """
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return model

# Personas endpoints
@router.get("/personas", response_model=PersonasResponse)
@version(2)
async def list_personas(
    service: ConfigService = Depends(get_config_service)
):
    """
    List all available personas that can be used with agents.
    
    Returns persona details including descriptions and capabilities.
    """
    return await service.get_personas()

@router.get("/personas/{persona_id}", response_model=PersonaInfo)
@version(2)
async def get_persona(
    persona_id: str,
    service: ConfigService = Depends(get_config_service)
):
    """
    Get detailed information about a specific persona.
    
    Returns the persona's configuration details or 404 if not found.
    """
    persona = await service.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return persona

# Tools endpoints
@router.get("/tools", response_model=ToolsResponse)
@version(2)
async def list_tools(
    service: ConfigService = Depends(get_config_service)
):
    """
    List all available tools that can be used with agents.
    
    Returns tool details categorized by type, with parameters and requirements.
    """
    return await service.get_tools()

@router.get("/tools/{tool_id}", response_model=ToolInfo)
@version(2)
async def get_tool(
    tool_id: str,
    service: ConfigService = Depends(get_config_service)
):
    """
    Get detailed information about a specific tool.
    
    Returns the tool's configuration details or 404 if not found.
    """
    tool = await service.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    return tool

# System config endpoint
@router.get("/system", response_model=SystemConfigResponse)
@version(2)
async def get_system_config(
    service: ConfigService = Depends(get_config_service)
):
    """
    Get combined system configuration including models, personas, and tools.
    
    Provides a complete overview of all available configuration options.
    """
    return await service.get_system_config()