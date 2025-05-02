# V2 API Implementation Plan - Step 1.3: Configuration Endpoints (Corrected)

## 1. Overview

In this step, we'll implement the configuration endpoints for the v2 API as outlined in our initial structure design. These endpoints will provide information about available models, personas, and tools, which are essential for clients to initialize and configure sessions. The configuration endpoints are read-only and don't require authentication, making them ideal for initial setup and discovery.

## 2. What are we changing?

We're implementing new v2 endpoints that will expose the existing configuration mechanisms through a clean, RESTful API:

1. **Config Router & Endpoints:**
   - Creating a dedicated router for configuration-related endpoints at `/api/v2/config/*`
   - Implementing endpoints for models, personas, tools, and a combined system configuration

2. **Config Services:**
   - Creating lightweight service classes that leverage existing methods in agent_manager.py, config_loader, and setup.py
   - Implementing appropriate caching for improved performance

3. **Config Models:**
   - Creating Pydantic models that accurately reflect the structure of the existing configuration data
   - Ensuring consistent response formats across endpoints

## 3. How are we changing it?

### 3.1 File Structure

```
src/agent_c_api/api/v2/config/
├── __init__.py           # Package init with router export
├── router.py             # Main router configuration
├── services.py           # Service layer wrapping existing functionality
└── models.py             # Pydantic models for config resources
```

### 3.2 Implementation Details

#### 3.2.1 Config Models (models.py)

```python
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class ModelParameter(BaseModel):
    """Parameter for a model configuration"""
    name: str
    type: str
    description: Optional[str] = None
    default: Optional[Any] = None

class ModelInfo(BaseModel):
    """Information about an available LLM model"""
    id: str
    name: str
    provider: str = Field(default="unknown")
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    parameters: List[ModelParameter] = Field(default_factory=list)
    allowed_inputs: List[str] = Field(default_factory=list)

class PersonaInfo(BaseModel):
    """Information about an available persona"""
    id: str
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None

class ToolParameter(BaseModel):
    """Parameter for a tool"""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False

class ToolInfo(BaseModel):
    """Information about an available tool"""
    id: str
    name: str
    description: Optional[str] = None
    category: str = "general"
    parameters: List[ToolParameter] = Field(default_factory=list)
    is_essential: bool = False

class ModelsResponse(BaseModel):
    """Response containing available models"""
    models: List[ModelInfo]

class PersonasResponse(BaseModel):
    """Response containing available personas"""
    personas: List[PersonaInfo]

class ToolsResponse(BaseModel):
    """Response containing available tools"""
    tools: List[ToolInfo]
    categories: List[str]
    essential_tools: List[str]

class SystemConfigResponse(BaseModel):
    """Combined system configuration response"""
    models: List[ModelInfo]
    personas: List[PersonaInfo]
    tools: List[ToolInfo]
    tool_categories: List[str]
    essential_tools: List[str]
```

#### 3.2.2 Config Services (services.py)

```python
import os
from typing import List, Dict, Optional, Any
from fastapi_cache.decorator import cache

from agent_c_api.config.config_loader import get_config_value
from agent_c_api.core.agent_manager import get_available_models, get_available_personas
from agent_c_api.core.setup import get_available_tools

from .models import (
    ModelInfo, PersonaInfo, ToolInfo, ModelParameter, ToolParameter,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

class ConfigService:
    """Service for retrieving configuration data from existing sources"""
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_models(self) -> ModelsResponse:
        """
        Get available models using the existing configuration mechanism
        """
        # Using the same approach as in v1/models.py
        models_config = get_config_value("MODELS_CONFIG", {})
        model_list = []
        
        # Process models in the same format as v1 API
        for vendor, vendor_models in models_config.items():
            for model_id, model_data in vendor_models.items():
                # Transform to our v2 model format
                parameters = []
                for param_name, param_data in model_data.get("parameters", {}).items():
                    parameters.append(ModelParameter(
                        name=param_name,
                        type=param_data.get("type", "string"),
                        description=param_data.get("description", ""),
                        default=param_data.get("default")
                    ))
                
                model_info = ModelInfo(
                    id=model_id,
                    name=model_data.get("label", model_id),
                    provider=vendor,
                    description=model_data.get("description", ""),
                    capabilities=model_data.get("capabilities", []),
                    parameters=parameters,
                    allowed_inputs=model_data.get("allowed_inputs", [])
                )
                model_list.append(model_info)
        
        return ModelsResponse(models=model_list)
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get a specific model by ID
        """
        models_response = self.get_models()
        for model in models_response.models:
            if model.id == model_id:
                return model
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_personas(self) -> PersonasResponse:
        """
        Get available personas using the existing file-based mechanism
        """
        # Using the same approach as in v1/personas.py
        personas = get_available_personas()
        persona_list = []
        
        for persona in personas:
            persona_info = PersonaInfo(
                id=persona.get("id", ""),
                name=persona.get("name", ""),
                description=persona.get("description", ""),
                file_path=persona.get("file_path", ""),
                content=persona.get("content", "")
            )
            persona_list.append(persona_info)
        
        return PersonasResponse(personas=persona_list)
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_persona(self, persona_id: str) -> Optional[PersonaInfo]:
        """
        Get a specific persona by ID
        """
        personas_response = self.get_personas()
        for persona in personas_response.personas:
            if persona.id == persona_id:
                return persona
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_tools(self) -> ToolsResponse:
        """
        Get available tools using the existing tool discovery mechanism
        """
        # Using the same approach as in v1/tools.py
        tools_data = get_available_tools()
        tool_list = []
        categories = set()
        essential_tools = []
        
        for tool in tools_data:
            # Extract category
            category = tool.get("category", "general")
            categories.add(category)
            
            # Check if essential
            is_essential = tool.get("essential", False)
            if is_essential:
                essential_tools.append(tool.get("id", ""))
            
            # Process parameters
            parameters = []
            for param in tool.get("parameters", []):
                parameters.append(ToolParameter(
                    name=param.get("name", ""),
                    type=param.get("type", "string"),
                    description=param.get("description", ""),
                    required=param.get("required", False)
                ))
            
            # Create tool info
            tool_info = ToolInfo(
                id=tool.get("id", ""),
                name=tool.get("name", ""),
                description=tool.get("description", ""),
                category=category,
                parameters=parameters,
                is_essential=is_essential
            )
            tool_list.append(tool_info)
        
        return ToolsResponse(
            tools=tool_list,
            categories=sorted(list(categories)),
            essential_tools=essential_tools
        )
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_tool(self, tool_id: str) -> Optional[ToolInfo]:
        """
        Get a specific tool by ID
        """
        tools_response = self.get_tools()
        for tool in tools_response.tools:
            if tool.id == tool_id:
                return tool
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    def get_system_config(self) -> SystemConfigResponse:
        """
        Get combined system configuration
        """
        models_response = self.get_models()
        personas_response = self.get_personas()
        tools_response = self.get_tools()
        
        return SystemConfigResponse(
            models=models_response.models,
            personas=personas_response.personas,
            tools=tools_response.tools,
            tool_categories=tools_response.categories,
            essential_tools=tools_response.essential_tools
        )
```

#### 3.2.3 Config Router (router.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi_versioning import version

from .services import ConfigService
from .models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

# Create router with prefix and tags
router = APIRouter(prefix="/config", tags=["configuration"])

# Dependency for getting the config service
def get_config_service():
    return ConfigService()

# Models endpoints
@router.get("/models", response_model=ModelsResponse)
@version(2)
async def list_models(
    service: ConfigService = Depends(get_config_service)
) -> ModelsResponse:
    """
    List all available LLM models that can be used with agents.
    
    Returns model details including provider, capabilities, and parameters.
    """
    return service.get_models()

@router.get("/models/{model_id}", response_model=ModelInfo)
@version(2)
async def get_model(
    model_id: str,
    service: ConfigService = Depends(get_config_service)
) -> ModelInfo:
    """
    Get detailed information about a specific model.
    
    Returns the model's configuration details or 404 if not found.
    """
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return model

# Personas endpoints
@router.get("/personas", response_model=PersonasResponse)
@version(2)
async def list_personas(
    service: ConfigService = Depends(get_config_service)
) -> PersonasResponse:
    """
    List all available personas that can be used with agents.
    
    Returns persona details including descriptions and capabilities.
    """
    return service.get_personas()

@router.get("/personas/{persona_id}", response_model=PersonaInfo)
@version(2)
async def get_persona(
    persona_id: str,
    service: ConfigService = Depends(get_config_service)
) -> PersonaInfo:
    """
    Get detailed information about a specific persona.
    
    Returns the persona's configuration details or 404 if not found.
    """
    persona = service.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return persona

# Tools endpoints
@router.get("/tools", response_model=ToolsResponse)
@version(2)
async def list_tools(
    service: ConfigService = Depends(get_config_service)
) -> ToolsResponse:
    """
    List all available tools that can be used with agents.
    
    Returns tool details categorized by type, with parameters and requirements.
    """
    return service.get_tools()

@router.get("/tools/{tool_id}", response_model=ToolInfo)
@version(2)
async def get_tool(
    tool_id: str,
    service: ConfigService = Depends(get_config_service)
) -> ToolInfo:
    """
    Get detailed information about a specific tool.
    
    Returns the tool's configuration details or 404 if not found.
    """
    tool = service.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    return tool

# System config endpoint
@router.get("/system", response_model=SystemConfigResponse)
@version(2)
async def get_system_config(
    service: ConfigService = Depends(get_config_service)
) -> SystemConfigResponse:
    """
    Get combined system configuration including models, personas, and tools.
    
    Provides a complete overview of all available configuration options.
    """
    return service.get_system_config()
```

#### 3.2.4 Config Package Init (__init__.py)

```python
from .router import router

__all__ = ['router']
```

### 3.3 Tests

We'll create tests that verify our endpoints correctly wrap the existing functionality:

#### 3.3.1 Testing the Router and Endpoints

```python
# src/agent_c_api/tests/v2/config/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from agent_c_api.main import app
from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.config.models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

client = TestClient(app)

@pytest.fixture
def mock_config_service():
    with patch('agent_c_api.api.v2.config.router.get_config_service') as mock_service_factory:
        mock_service = MagicMock(spec=ConfigService)
        mock_service_factory.return_value = mock_service
        yield mock_service

def test_list_models(mock_config_service):
    # Set up mock response
    mock_config_service.get_models.return_value = ModelsResponse(
        models=[
            ModelInfo(
                id="gpt-4",
                name="GPT-4",
                provider="openai",
                description="Advanced language model",
                capabilities=["text"],
                parameters=[]
            )
        ]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/models")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) == 1
    assert data["models"][0]["id"] == "gpt-4"
    assert data["models"][0]["provider"] == "openai"
    
    # Verify service was called
    mock_config_service.get_models.assert_called_once()

def test_get_model_success(mock_config_service):
    # Set up mock response
    mock_config_service.get_model.return_value = ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="openai",
        description="Advanced language model",
        capabilities=["text"],
        parameters=[]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/models/gpt-4")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "gpt-4"
    assert data["provider"] == "openai"
    
    # Verify service was called
    mock_config_service.get_model.assert_called_once_with("gpt-4")

def test_get_model_not_found(mock_config_service):
    # Set up mock response
    mock_config_service.get_model.return_value = None
    
    # Test endpoint
    response = client.get("/api/v2/config/models/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

# Similar tests for personas and tools endpoints

def test_get_system_config(mock_config_service):
    # Set up mock response
    mock_config_service.get_system_config.return_value = SystemConfigResponse(
        models=[
            ModelInfo(id="gpt-4", name="GPT-4", provider="openai")
        ],
        personas=[
            PersonaInfo(id="default", name="Default Persona")
        ],
        tools=[
            ToolInfo(id="search", name="Search Tool", category="web")
        ],
        tool_categories=["web", "utility"],
        essential_tools=["search"]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/system")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "personas" in data
    assert "tools" in data
    assert "tool_categories" in data
    assert "essential_tools" in data
```

#### 3.3.2 Testing the Service Layer

```python
# src/agent_c_api/tests/v2/config/test_services.py
import pytest
from unittest.mock import patch, MagicMock

from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.config.models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse
)

@pytest.fixture
def mock_config_loader():
    with patch('agent_c_api.config.config_loader.get_config_value') as mock_get_config:
        # Sample models config structure - simplified for testing
        mock_get_config.return_value = {
            "openai": {
                "gpt-4": {
                    "label": "GPT-4",
                    "description": "Advanced language model",
                    "capabilities": ["text"],
                    "parameters": {
                        "temperature": {
                            "type": "float",
                            "default": 0.7,
                            "description": "Controls randomness"
                        }
                    },
                    "allowed_inputs": ["text"]
                }
            }
        }
        yield mock_get_config

@pytest.fixture
def mock_agent_manager():
    with patch('agent_c_api.core.agent_manager.get_available_personas') as mock_personas:
        # Sample personas structure
        mock_personas.return_value = [
            {
                "id": "default",
                "name": "Default Assistant",
                "description": "Standard assistant persona",
                "file_path": "/path/to/default.md",
                "content": "You are a helpful assistant."
            }
        ]
        yield mock_personas

@pytest.fixture
def mock_tools():
    with patch('agent_c_api.core.setup.get_available_tools') as mock_tools:
        # Sample tools structure
        mock_tools.return_value = [
            {
                "id": "search",
                "name": "Search Tool",
                "description": "Search the web",
                "category": "web",
                "essential": True,
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "Search query",
                        "required": True
                    }
                ]
            }
        ]
        yield mock_tools

def test_get_models(mock_config_loader):
    service = ConfigService()
    result = service.get_models()
    
    assert isinstance(result, ModelsResponse)
    assert len(result.models) == 1
    assert result.models[0].id == "gpt-4"
    assert result.models[0].name == "GPT-4"
    assert result.models[0].provider == "openai"
    assert len(result.models[0].parameters) == 1
    assert result.models[0].parameters[0].name == "temperature"
    assert result.models[0].parameters[0].type == "float"

def test_get_model(mock_config_loader):
    service = ConfigService()
    
    # Test existing model
    model = service.get_model("gpt-4")
    assert model is not None
    assert model.id == "gpt-4"
    
    # Test non-existent model
    model = service.get_model("nonexistent")
    assert model is None

def test_get_personas(mock_agent_manager):
    service = ConfigService()
    result = service.get_personas()
    
    assert isinstance(result, PersonasResponse)
    assert len(result.personas) == 1
    assert result.personas[0].id == "default"
    assert result.personas[0].name == "Default Assistant"
    assert result.personas[0].content == "You are a helpful assistant."

def test_get_tools(mock_tools):
    service = ConfigService()
    result = service.get_tools()
    
    assert isinstance(result, ToolsResponse)
    assert len(result.tools) == 1
    assert result.tools[0].id == "search"
    assert result.tools[0].category == "web"
    assert result.tools[0].is_essential == True
    assert len(result.tools[0].parameters) == 1
    assert result.categories == ["web"]
    assert result.essential_tools == ["search"]

def test_get_system_config(mock_config_loader, mock_agent_manager, mock_tools):
    service = ConfigService()
    result = service.get_system_config()
    
    assert len(result.models) == 1
    assert len(result.personas) == 1
    assert len(result.tools) == 1
    assert result.tool_categories == ["web"]
    assert result.essential_tools == ["search"]
```

## 4. Why are we changing it?

We're implementing these configuration endpoints to provide a clean, RESTful interface to the existing configuration data. The benefits include:

1. **Consistent API Design**: The v2 configuration endpoints follow a consistent RESTful pattern, making the API more intuitive for developers.

2. **Resource-Oriented Structure**: Resources are clearly identified and exposed through appropriate URLs, improving discoverability.

3. **Proper Caching**: Utilizing FastAPI's caching mechanism for these relatively static resources improves performance.

4. **Self-Documented API**: The OpenAPI documentation generated from these endpoints will help developers understand the available options.

5. **Backward Compatibility**: By leveraging the existing configuration mechanisms, we ensure backward compatibility with the current system.

6. **Simplified Client Development**: Clients can easily discover available models, personas, and tools without complex configuration.

7. **Proper Error Handling**: Consistent HTTP status codes for error conditions improve client error handling.

## 5. Implementation Steps

1. Create the basic directory structure and __init__.py files
2. Implement the models.py file with appropriate Pydantic models
3. Implement the services.py file with the ConfigService class
4. Implement the router.py file with all endpoint definitions
5. Write tests to verify functionality
6. Connect the router to the main API structure

## 6. Completion Criteria

- All configuration endpoints are implemented and tested
- Endpoints return data consistent with the existing v1 API functionality
- Appropriate caching is implemented for performance
- Tests verify both success and error scenarios
- Documentation is generated correctly via OpenAPI
- Endpoints work with the existing configuration mechanisms

## 7. Potential Risks and Mitigations

1. **Risk**: Changes to underlying configuration mechanisms might break the new endpoints.
   **Mitigation**: Comprehensive tests that verify correct behavior and proper error handling.

2. **Risk**: Caching might result in stale data if configurations change.
   **Mitigation**: Keep cache TTL reasonably short (5 minutes) and implement cache invalidation if needed.
