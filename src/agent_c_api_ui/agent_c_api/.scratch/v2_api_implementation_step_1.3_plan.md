# V2 API Implementation Plan - Step 1.3: Configuration Endpoints

## 1. Overview

In this step, we'll implement the configuration endpoints for the v2 API. These endpoints will provide information about available models, personas, and tools, which are essential for clients to initialize and configure sessions. The configuration endpoints are read-only and don't require authentication, making them ideal for initial setup and discovery.

## 2. What are we changing?

We'll be creating the following new components:

1. **Config Router & Endpoints:**
   - Creating a dedicated router for configuration-related endpoints
   - Implementing endpoints for models, personas, and tools information

2. **Config Services:**
   - Creating service classes to fetch and process configuration data
   - Implementing caching mechanisms for performance optimization

3. **Utility Functions:**
   - Adding helper functions for consistent response formatting
   - Implementing pagination support for listing endpoints

## 3. How are we changing it?

### 3.1 File Structure

```
src/agent_c_api/api/v2/config/
├── __init__.py           # Package init with router export
├── router.py             # Main router configuration
├── endpoints.py          # Endpoint implementations
├── services.py           # Service layer for business logic
└── cache.py              # Cache implementations for config data
```

### 3.2 Implementation Details

#### 3.2.1 Config Router (router.py)

```python
from fastapi import APIRouter
from fastapi_versioning import version
from fastapi_pagination import Page

from . import endpoints
from ..models.agent_models import ModelInfo, PersonaInfo
from ..models.tool_models import ToolInfo

router = APIRouter(prefix="/config", tags=["configuration"])

# Models endpoints
router.add_api_route(
    "/models",
    endpoints.list_models,
    methods=["GET"],
    response_model=Page[ModelInfo],
    summary="List available models",
    description="Retrieve a paginated list of available LLM models."
)

router.add_api_route(
    "/models/{model_id}",
    endpoints.get_model,
    methods=["GET"],
    response_model=ModelInfo,
    summary="Get model details",
    description="Retrieve detailed information about a specific model."
)

# Personas endpoints
router.add_api_route(
    "/personas",
    endpoints.list_personas,
    methods=["GET"],
    response_model=Page[PersonaInfo],
    summary="List available personas",
    description="Retrieve a paginated list of available personas."
)

router.add_api_route(
    "/personas/{persona_id}",
    endpoints.get_persona,
    methods=["GET"],
    response_model=PersonaInfo,
    summary="Get persona details",
    description="Retrieve detailed information about a specific persona."
)

# Tools endpoints
router.add_api_route(
    "/tools",
    endpoints.list_tools,
    methods=["GET"],
    response_model=Page[ToolInfo],
    summary="List available tools",
    description="Retrieve a paginated list of available tools."
)

router.add_api_route(
    "/tools/{tool_id}",
    endpoints.get_tool,
    methods=["GET"],
    response_model=ToolInfo,
    summary="Get tool details",
    description="Retrieve detailed information about a specific tool."
)
```

#### 3.2.2 Config Endpoints (endpoints.py)

```python
from fastapi import HTTPException, Depends, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate

from .services import ConfigService
from ..models.agent_models import ModelInfo, PersonaInfo
from ..models.tool_models import ToolInfo

async def get_config_service():
    """Dependency for config service"""
    return ConfigService()

async def list_models(
    search: str = Query(None, description="Optional search term for model name or description"),
    provider: str = Query(None, description="Filter by provider"),
    service: ConfigService = Depends(get_config_service)
) -> Page[ModelInfo]:
    """List available models with optional filtering"""
    return await service.get_models(search=search, provider=provider)

async def get_model(
    model_id: str,
    service: ConfigService = Depends(get_config_service)
) -> ModelInfo:
    """Get details for a specific model"""
    model = await service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return model

async def list_personas(
    search: str = Query(None, description="Optional search term for persona name or description"),
    service: ConfigService = Depends(get_config_service)
) -> Page[PersonaInfo]:
    """List available personas with optional filtering"""
    return await service.get_personas(search=search)

async def get_persona(
    persona_id: str,
    service: ConfigService = Depends(get_config_service)
) -> PersonaInfo:
    """Get details for a specific persona"""
    persona = await service.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return persona

async def list_tools(
    search: str = Query(None, description="Optional search term for tool name or description"),
    category: str = Query(None, description="Filter by tool category"),
    service: ConfigService = Depends(get_config_service)
) -> Page[ToolInfo]:
    """List available tools with optional filtering"""
    return await service.get_tools(search=search, category=category)

async def get_tool(
    tool_id: str,
    service: ConfigService = Depends(get_config_service)
) -> ToolInfo:
    """Get details for a specific tool"""
    tool = await service.get_tool_by_id(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    return tool
```

#### 3.2.3 Config Services (services.py)

```python
from typing import List, Optional, Dict, Any
from fastapi_pagination import Page
from fastapi_cache.decorator import cache

from agent_c_api.core.agent_manager import get_available_models, get_available_personas
from agent_c_api.core.setup import get_available_tools
from ..models.agent_models import ModelInfo, PersonaInfo, ModelParameter
from ..models.tool_models import ToolInfo, ToolParameter

class ConfigService:
    """Service for retrieving configuration data"""
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_models(self, search: Optional[str] = None, provider: Optional[str] = None) -> Page[ModelInfo]:
        """Get available models with optional filtering"""
        models = get_available_models()
        
        # Apply filters
        filtered_models = []
        for model in models:
            if provider and model.get('provider', '').lower() != provider.lower():
                continue
                
            if search:
                search_lower = search.lower()
                name = model.get('name', '').lower()
                description = model.get('description', '').lower()
                if search_lower not in name and search_lower not in description:
                    continue
            
            # Convert to ModelInfo
            model_info = ModelInfo(
                id=model['id'],
                name=model['name'],
                provider=model.get('provider', 'unknown'),
                description=model.get('description', ''),
                capabilities=model.get('capabilities', []),
                parameters=[
                    ModelParameter(
                        name=param['name'],
                        type=param['type'],
                        description=param.get('description', ''),
                        value=param.get('default')
                    )
                    for param in model.get('parameters', [])
                ]
            )
            filtered_models.append(model_info)
            
        # Return paginated results
        return Page[ModelInfo](items=filtered_models, total=len(filtered_models), page=1, size=len(filtered_models))
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """Get a specific model by ID"""
        models = get_available_models()
        for model in models:
            if model['id'] == model_id:
                return ModelInfo(
                    id=model['id'],
                    name=model['name'],
                    provider=model.get('provider', 'unknown'),
                    description=model.get('description', ''),
                    capabilities=model.get('capabilities', []),
                    parameters=[
                        ModelParameter(
                            name=param['name'],
                            type=param['type'],
                            description=param.get('description', ''),
                            value=param.get('default')
                        )
                        for param in model.get('parameters', [])
                    ]
                )
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_personas(self, search: Optional[str] = None) -> Page[PersonaInfo]:
        """Get available personas with optional filtering"""
        personas = get_available_personas()
        
        # Apply filters
        filtered_personas = []
        for persona in personas:
            if search:
                search_lower = search.lower()
                name = persona.get('name', '').lower()
                description = persona.get('description', '').lower()
                if search_lower not in name and search_lower not in description:
                    continue
            
            # Convert to PersonaInfo
            persona_info = PersonaInfo(
                id=persona['id'],
                name=persona['name'],
                description=persona.get('description', ''),
                capabilities=persona.get('capabilities', []),
                system_message=persona.get('system_message', None)
            )
            filtered_personas.append(persona_info)
            
        # Return paginated results
        return Page[PersonaInfo](items=filtered_personas, total=len(filtered_personas), page=1, size=len(filtered_personas))
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_persona_by_id(self, persona_id: str) -> Optional[PersonaInfo]:
        """Get a specific persona by ID"""
        personas = get_available_personas()
        for persona in personas:
            if persona['id'] == persona_id:
                return PersonaInfo(
                    id=persona['id'],
                    name=persona['name'],
                    description=persona.get('description', ''),
                    capabilities=persona.get('capabilities', []),
                    system_message=persona.get('system_message', None)
                )
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_tools(self, search: Optional[str] = None, category: Optional[str] = None) -> Page[ToolInfo]:
        """Get available tools with optional filtering"""
        tools = get_available_tools()
        
        # Apply filters
        filtered_tools = []
        for tool in tools:
            if category and tool.get('category', '').lower() != category.lower():
                continue
                
            if search:
                search_lower = search.lower()
                name = tool.get('name', '').lower()
                description = tool.get('description', '').lower()
                if search_lower not in name and search_lower not in description:
                    continue
            
            # Convert to ToolInfo
            tool_info = ToolInfo(
                id=tool['id'],
                name=tool['name'],
                description=tool.get('description', ''),
                category=tool.get('category', 'general'),
                parameters=[
                    ToolParameter(
                        name=param['name'],
                        type=param['type'],
                        description=param.get('description', ''),
                        required=param.get('required', False)
                    )
                    for param in tool.get('parameters', [])
                ]
            )
            filtered_tools.append(tool_info)
            
        # Return paginated results
        return Page[ToolInfo](items=filtered_tools, total=len(filtered_tools), page=1, size=len(filtered_tools))
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_tool_by_id(self, tool_id: str) -> Optional[ToolInfo]:
        """Get a specific tool by ID"""
        tools = get_available_tools()
        for tool in tools:
            if tool['id'] == tool_id:
                return ToolInfo(
                    id=tool['id'],
                    name=tool['name'],
                    description=tool.get('description', ''),
                    category=tool.get('category', 'general'),
                    parameters=[
                        ToolParameter(
                            name=param['name'],
                            type=param['type'],
                            description=param.get('description', ''),
                            required=param.get('required', False)
                        )
                        for param in tool.get('parameters', [])
                    ]
                )
        return None
```

#### 3.2.4 Config Package Init (__init__.py)

```python
from .router import router

__all__ = ['router']
```

### 3.3 Tests

We'll create comprehensive tests for the configuration endpoints:

#### 3.3.1 Testing the Router and Endpoints

```python
# src/agent_c_api/tests/v2/config/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from agent_c_api.main import app
from agent_c_api.api.v2.config.services import ConfigService

client = TestClient(app)

@pytest.fixture
def mock_config_service():
    with patch('agent_c_api.api.v2.config.endpoints.get_config_service') as mock_service:
        service = MagicMock()
        mock_service.return_value = service
        yield service

def test_list_models(mock_config_service):
    # Setup mock responses
    mock_config_service.get_models.return_value = {
        "items": [
            {"id": "model1", "name": "Model 1", "provider": "openai"}
        ],
        "total": 1,
        "page": 1,
        "size": 10
    }
    
    # Test endpoint
    response = client.get("/api/v2/config/models")
    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == "model1"
    
    # Verify filters are passed correctly
    response = client.get("/api/v2/config/models?search=test&provider=openai")
    assert response.status_code == 200
    mock_config_service.get_models.assert_called_with(search="test", provider="openai")

def test_get_model(mock_config_service):
    # Setup mock responses
    mock_config_service.get_model_by_id.return_value = {"id": "model1", "name": "Model 1"}
    
    # Test endpoint
    response = client.get("/api/v2/config/models/model1")
    assert response.status_code == 200
    assert response.json()["id"] == "model1"
    
    # Test not found
    mock_config_service.get_model_by_id.return_value = None
    response = client.get("/api/v2/config/models/nonexistent")
    assert response.status_code == 404

# Similar tests for personas and tools endpoints
```

#### 3.3.2 Testing the Service Layer

```python
# src/agent_c_api/tests/v2/config/test_services.py
import pytest
from unittest.mock import patch, MagicMock

from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.models.agent_models import ModelInfo, PersonaInfo
from agent_c_api.api.v2.models.tool_models import ToolInfo

@pytest.fixture
def mock_agent_manager():
    with patch('agent_c_api.core.agent_manager.get_available_models') as mock_models, \
         patch('agent_c_api.core.agent_manager.get_available_personas') as mock_personas, \
         patch('agent_c_api.core.setup.get_available_tools') as mock_tools:
        mock_models.return_value = [
            {
                "id": "model1",
                "name": "Test Model",
                "provider": "openai",
                "description": "A test model",
                "capabilities": ["text"],
                "parameters": [
                    {"name": "temperature", "type": "float", "description": "Temperature parameter", "default": 0.7}
                ]
            }
        ]
        mock_personas.return_value = [
            {
                "id": "persona1",
                "name": "Test Persona",
                "description": "A test persona",
                "capabilities": ["coding"],
                "system_message": "You are a test persona"
            }
        ]
        mock_tools.return_value = [
            {
                "id": "tool1",
                "name": "Test Tool",
                "description": "A test tool",
                "category": "utilities",
                "parameters": [
                    {"name": "param1", "type": "string", "description": "Parameter 1", "required": True}
                ]
            }
        ]
        yield

@pytest.mark.asyncio
async def test_get_models(mock_agent_manager):
    service = ConfigService()
    result = await service.get_models()
    assert len(result.items) == 1
    assert result.items[0].id == "model1"
    assert result.items[0].name == "Test Model"
    assert len(result.items[0].parameters) == 1
    assert result.items[0].parameters[0].name == "temperature"

@pytest.mark.asyncio
async def test_get_model_by_id(mock_agent_manager):
    service = ConfigService()
    result = await service.get_model_by_id("model1")
    assert result is not None
    assert result.id == "model1"
    assert result.name == "Test Model"
    
    # Test not found
    result = await service.get_model_by_id("nonexistent")
    assert result is None

# Similar tests for personas and tools methods
```

## 4. Why are we changing it?

Implementing these configuration endpoints provides several benefits:

1. **Client Discovery:** Allows clients to discover available models, personas, and tools dynamically.

2. **Decoupling:** Separates configuration management from session management, following the Single Responsibility Principle.

3. **Performance:** By implementing caching for these relatively static resources, we improve API response times.

4. **Self-Documentation:** The API becomes self-documenting, allowing frontend developers to discover capabilities without additional documentation.

5. **Versioning Support:** The configuration endpoints support our versioning strategy, ensuring backward compatibility.

## 5. Testing Strategy

1. **Unit Tests:** Test individual components (services, endpoint functions) in isolation.

2. **Integration Tests:** Test the endpoints with mocked dependencies.

3. **End-to-End Tests:** Test the complete flow through the API with real dependencies.

4. **Performance Tests:** Verify that caching is working correctly and improves response times.

## 6. Implementation Steps

1. Create the basic structure (folders and package files)
2. Implement the service layer with appropriate mocks for testing
3. Implement the router and endpoint functions
4. Write comprehensive tests for all components
5. Connect the router to the main API
6. Verify with manual testing

## 7. Completion Criteria

- All endpoints are implemented and tested
- Responses match the defined models
- Caching is working correctly
- Tests pass with good coverage
- Documentation is generated correctly via OpenAPI

## 8. Potential Risks and Mitigations

1. **Risk:** Integration with the core agent management system may be challenging.
   **Mitigation:** Create clear interfaces and tests to ensure compatibility.

2. **Risk:** Caching could lead to stale data if configurations change frequently.
   **Mitigation:** Implement a cache invalidation strategy and keep cache TTL reasonably short.

3. **Risk:** Performance issues with large datasets.
   **Mitigation:** Implement proper pagination and filtering to limit result sets.