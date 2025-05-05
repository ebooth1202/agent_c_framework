from fastapi import APIRouter, HTTPException, Depends, Path, Query
from typing import Optional
# Removed fastapi_versioning import - using directory structure for versioning

from .services import ConfigService
from agent_c_api.api.v2.models.config_models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

# Create router with prefix and tags
router = APIRouter(
    prefix="/config",  # Prefix matches the module name
    tags=["config"],    # Tag for grouping in OpenAPI docs
    responses={
        404: {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Item not found"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Internal server error",
                            "error_code": "SERVER_ERROR",
                            "message": "An unexpected error occurred while processing the request"
                        }
                    }
                }
            }
        }
    }
)

# Dependency for getting the config service
def get_config_service():
    return ConfigService()

# Models endpoints
@router.get("/models", 
           response_model=ModelsResponse,
           summary="List Available Models",
           description="Returns a list of all available language models that can be used with Agent C.")
# Version is determined by directory structure
async def list_models(
    service: ConfigService = Depends(get_config_service)
):
    """
    List all available LLM models that can be used with agents.
    
    This endpoint provides information about all language models configured for use with Agent C.
    It includes details such as model capabilities, configuration parameters, and input types.
    
    Returns:
        ModelsResponse: A list of available models with their details
        
    Example:
        ```python
        import requests
        
        response = requests.get("https://your-agent-c-instance.com/api/v2/config/models")
        models = response.json()["models"]
        ```
    """
    return await service.get_models()

@router.get("/models/{model_id}", 
           response_model=ModelInfo,
           summary="Get Model Details",
           description="Returns detailed information about a specific language model.")
# Version is determined by directory structure
async def get_model(
    model_id: str = Path(..., description="The unique identifier of the model to retrieve"),
    service: ConfigService = Depends(get_config_service)
):
    """
    Get detailed information about a specific model.
    
    This endpoint provides detailed information about a specific language model identified by its ID.
    It includes full details about capabilities, configuration parameters, and supported input types.
    
    Args:
        model_id: The unique identifier of the model to retrieve
        
    Returns:
        ModelInfo: Detailed information about the requested model
        
    Raises:
        HTTPException: 404 error if the model is not found
        
    Example:
        ```python
        import requests
        
        model_id = "gpt-4"
        response = requests.get(f"https://your-agent-c-instance.com/api/v2/config/models/{model_id}")
        model = response.json()
        ```
    """
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "MODEL_NOT_FOUND",
                "error_code": "MODEL_NOT_FOUND",
                "message": f"Model {model_id} not found",
                "params": {"model_id": model_id}
            }
        )
    return model

# Personas endpoints
@router.get("/personas", 
           response_model=PersonasResponse,
           summary="List Available Personas",
           description="Returns a list of all available personas that can be used with Agent C.")
# Version is determined by directory structure
async def list_personas(
    service: ConfigService = Depends(get_config_service)
):
    """
    List all available personas that can be used with agents.
    
    This endpoint provides information about all personas configured for use with Agent C.
    Personas define the agent's personality, tone, and behavioral characteristics.
    
    Returns:
        PersonasResponse: A list of available personas with their details
        
    Example:
        ```python
        import requests
        
        response = requests.get("https://your-agent-c-instance.com/api/v2/config/personas")
        personas = response.json()["personas"]
        ```
    """
    return await service.get_personas()

@router.get("/personas/{persona_id}", 
           response_model=PersonaInfo,
           summary="Get Persona Details",
           description="Returns detailed information about a specific persona.")
# Version is determined by directory structure
async def get_persona(
    persona_id: str = Path(..., description="The unique identifier of the persona to retrieve"),
    service: ConfigService = Depends(get_config_service)
):
    """
    Get detailed information about a specific persona.
    
    This endpoint provides detailed information about a specific persona identified by its ID.
    It includes the persona's name, description, and may include the actual persona prompt content.
    
    Args:
        persona_id: The unique identifier of the persona to retrieve
        
    Returns:
        PersonaInfo: Detailed information about the requested persona
        
    Raises:
        HTTPException: 404 error if the persona is not found
        
    Example:
        ```python
        import requests
        
        persona_id = "coder"
        response = requests.get(f"https://your-agent-c-instance.com/api/v2/config/personas/{persona_id}")
        persona = response.json()
        ```
    """
    persona = await service.get_persona(persona_id)
    if not persona:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "PERSONA_NOT_FOUND",
                "error_code": "PERSONA_NOT_FOUND",
                "message": f"Persona {persona_id} not found",
                "params": {"persona_id": persona_id}
            }
        )
    return persona

# Tools endpoints
@router.get("/tools", 
           response_model=ToolsResponse,
           summary="List Available Tools",
           description="Returns a list of all available tools that can be used with Agent C.")
# Version is determined by directory structure
async def list_tools(
    category: Optional[str] = Query(None, description="Filter tools by category"),
    service: ConfigService = Depends(get_config_service)
):
    """
    List all available tools that can be used with agents.
    
    This endpoint provides information about all tools configured for use with Agent C.
    Tools extend the agent's capabilities, allowing it to perform specific tasks like web searches,
    calculations, or file operations.
    
    Args:
        category: Optional filter to return only tools from a specific category
        
    Returns:
        ToolsResponse: A list of available tools with their details, organized by category
        
    Example:
        ```python
        import requests
        
        # Get all tools
        response = requests.get("https://your-agent-c-instance.com/api/v2/config/tools")
        tools = response.json()["tools"]
        
        # Get tools filtered by category
        response = requests.get("https://your-agent-c-instance.com/api/v2/config/tools?category=web")
        web_tools = response.json()["tools"]
        ```
    """
    # Note: The actual implementation would use the category parameter to filter results
    # This is a placeholder for demonstration purposes
    return await service.get_tools()

@router.get("/tools/{tool_id}", 
           response_model=ToolInfo,
           summary="Get Tool Details",
           description="Returns detailed information about a specific tool.")
# Version is determined by directory structure
async def get_tool(
    tool_id: str = Path(..., description="The unique identifier of the tool to retrieve"),
    service: ConfigService = Depends(get_config_service)
):
    """
    Get detailed information about a specific tool.
    
    This endpoint provides detailed information about a specific tool identified by its ID.
    It includes the tool's name, description, category, parameters, and whether it's considered essential.
    
    Args:
        tool_id: The unique identifier of the tool to retrieve
        
    Returns:
        ToolInfo: Detailed information about the requested tool
        
    Raises:
        HTTPException: 404 error if the tool is not found
        
    Example:
        ```python
        import requests
        
        tool_id = "web_search"
        response = requests.get(f"https://your-agent-c-instance.com/api/v2/config/tools/{tool_id}")
        tool = response.json()
        ```
    """
    tool = await service.get_tool(tool_id)
    if not tool:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "TOOL_NOT_FOUND",
                "error_code": "TOOL_NOT_FOUND",
                "message": f"Tool {tool_id} not found",
                "params": {"tool_id": tool_id}
            }
        )
    return tool

# System config endpoint
@router.get("/system", 
           response_model=SystemConfigResponse,
           summary="Get System Configuration",
           description="Returns a combined configuration with models, personas, and tools.")
# Version is determined by directory structure
async def get_system_config(
    service: ConfigService = Depends(get_config_service)
):
    """
    Get combined system configuration including models, personas, and tools.
    
    This endpoint provides a consolidated view of all configuration options in a single request.
    It's useful for initializing client applications with all available options at once.
    
    The response includes:
    - Available models with their capabilities
    - Available personas with their descriptions
    - Available tools organized by category
    - List of essential tools that should be enabled by default
    
    Returns:
        SystemConfigResponse: Combined configuration data including models, personas, and tools
        
    Example:
        ```python
        import requests
        
        response = requests.get("https://your-agent-c-instance.com/api/v2/config/system")
        config = response.json()
        models = config["models"]
        personas = config["personas"]
        tools = config["tools"]
        ```
    """
    try:
        return await service.get_system_config()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Failed to retrieve system configuration",
                "error_code": "CONFIG_RETRIEVAL_ERROR",
                "message": str(e)
            }
        )