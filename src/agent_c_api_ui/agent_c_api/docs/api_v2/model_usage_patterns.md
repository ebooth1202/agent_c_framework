# API v2 Model Usage Patterns

This document provides examples of common usage patterns for working with the API v2 models, including extension patterns, composition techniques, and validation approaches.

## Table of Contents

1. [Basic Model Usage](#basic-model-usage)
2. [Model Extension Patterns](#model-extension-patterns)
3. [Model Composition Patterns](#model-composition-patterns)
4. [Using Model Registry](#using-model-registry)
5. [Model Validation Techniques](#model-validation-techniques)
6. [Working with Response Models](#working-with-response-models)
7. [Testing Models](#testing-models)

## Basic Model Usage

### Creating and Using Models

```python
from agent_c_api.api.v2.models.session_models import SessionCreate, AgentConfig

# Creating a model instance
session_create = SessionCreate(
    model_id="gpt-4",
    persona_id="researcher",
    name="Research Session",
    metadata={"project": "climate-analysis"}
)

# Accessing fields
model_id = session_create.model_id  # "gpt-4"

# Converting to dictionary
session_dict = session_create.model_dump()

# Converting to JSON
session_json = session_create.model_dump_json()

# Creating from dictionary
config_dict = {
    "model_id": "gpt-4",
    "persona_id": "architect",
    "temperature": 0.7,
    "tools": ["search", "code_analysis"]
}
config = AgentConfig(**config_dict)
```

## Model Extension Patterns

### Inheritance

Use inheritance when a model is a specialized version of another model:

```python
from pydantic import BaseModel, Field
from typing import Optional, List

# Base model
class BasePersona(BaseModel):
    id: str = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")

# Extended model
class SpecializedPersona(BasePersona):
    capabilities: List[str] = Field(default_factory=list, description="Specialized capabilities")
    domain_expertise: Optional[str] = Field(None, description="Domain of expertise")
```

### Extension with Config Customization

```python
from pydantic import BaseModel, Field, ConfigDict

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")

class EnhancedResponse(BaseResponse):
    data: dict = Field(default_factory=dict, description="Response data")
    
    # Customize the configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Operation completed",
                "data": {"result_id": "12345"}
            }
        }
    )
```

## Model Composition Patterns

### Using Models as Fields

Use composition when one model contains another model as a field:

```python
from pydantic import BaseModel, Field
from agent_c_api.api.v2.models.session_models import AgentConfig

class SessionWithAgent(BaseModel):
    session_id: str = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    agent_config: AgentConfig = Field(..., description="Agent configuration")
```

### Composition with Optional Models

```python
from typing import Optional
from pydantic import BaseModel, Field
from agent_c_api.api.v2.models.tool_models import ToolInfo

class ToolUsage(BaseModel):
    tool_id: str = Field(..., description="Tool ID")
    usage_count: int = Field(0, description="Number of times the tool was used")
    last_used: Optional[str] = Field(None, description="Timestamp of last usage")
    tool_info: Optional[ToolInfo] = Field(None, description="Detailed tool information")
```

## Using Model Registry

### Finding Models by Name

```python
from agent_c_api.api.v2.models.registry import get_model_by_name, get_type_by_name

# Get a specific model class by name
session_detail_class = get_model_by_name("SessionDetail")

# Create an instance of the dynamically retrieved class
session = session_detail_class(id="tiger-castle", model_id="gpt-4", ...)

# Get any type (model or enum)
event_type_enum = get_type_by_name("ChatEventType")
```

### Working with Domain Models

```python
from agent_c_api.api.v2.models.registry import list_models_by_domain

# Get all models in a specific domain
session_models = list_models_by_domain("session")

# Display available models
for model_class in session_models:
    print(f"Model: {model_class.__name__}")
    print(f"Description: {model_class.__doc__.strip()}")
    print("---")
```

### Verifying Model Integrity

```python
from agent_c_api.api.v2.models.registry import verify_no_duplicate_models

# Check for duplicate models (useful in tests)
assert verify_no_duplicate_models(), "Duplicate models found in registry"
```

## Model Validation Techniques

### Field Validators

```python
from pydantic import BaseModel, Field, field_validator

class TemperatureSettings(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0, description="Temperature value (0.0-1.0)")
    
    @field_validator('value')
    def check_value_range(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {v}")
        return v
```

### Custom Validation Logic

```python
from typing import List
from pydantic import BaseModel, Field, model_validator

class ToolSelection(BaseModel):
    tool_ids: List[str] = Field(..., description="IDs of tools to enable")
    allow_external: bool = Field(False, description="Whether to allow external tools")
    
    @model_validator(mode='after')
    def check_external_tools(self):
        if not self.allow_external and any(t.startswith('external:') for t in self.tool_ids):
            raise ValueError("External tools are not allowed with current settings")
        return self
```

## Working with Response Models

### Creating API Responses

```python
from fastapi import APIRouter, Depends, HTTPException
from agent_c_api.api.v2.models.response_models import APIResponse
from agent_c_api.api.v2.models.session_models import SessionDetail

router = APIRouter()

@router.get("/sessions/{session_id}", response_model=APIResponse)
async def get_session(session_id: str):
    try:
        # Get session logic here...
        session = SessionDetail(id=session_id, ...)
        
        return APIResponse(
            status="success",
            message="Session retrieved successfully",
            data=session.model_dump()
        )
    except Exception as e:
        return APIResponse(
            status="error",
            message=str(e)
        )
```

### Paginated Responses

```python
from typing import List
from agent_c_api.api.v2.models.response_models import PaginatedResponse, PaginationMeta
from agent_c_api.api.v2.models.session_models import SessionSummary

def get_paginated_sessions(page: int = 1, page_size: int = 10) -> PaginatedResponse:
    # Fetch data logic here...
    sessions: List[SessionSummary] = [...]
    total_count = 100  # example total
    
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=(total_count + page_size - 1) // page_size
    )
    
    return PaginatedResponse(
        items=sessions,
        pagination=pagination
    )
```

## Testing Models

### Basic Model Testing

```python
import pytest
from agent_c_api.api.v2.models.session_models import SessionCreate

def test_session_create_model():
    # Test valid creation
    session = SessionCreate(
        model_id="gpt-4",
        persona_id="researcher",
        name="Test Session"
    )
    assert session.model_id == "gpt-4"
    assert session.persona_id == "researcher"
    
    # Test validation error
    with pytest.raises(ValueError):
        SessionCreate(model_id=None, persona_id="researcher")
```

### Testing Model Conversion

```python
from agent_c_api.api.v2.models.session_models import AgentConfig

def test_model_serialization():
    # Create model instance
    config = AgentConfig(
        model_id="gpt-4",
        persona_id="researcher",
        temperature=0.7,
        tools=["search", "code_analysis"]
    )
    
    # Test serialization
    config_dict = config.model_dump()
    assert config_dict["model_id"] == "gpt-4"
    assert config_dict["temperature"] == 0.7
    
    # Test deserialization
    config2 = AgentConfig(**config_dict)
    assert config2.model_id == config.model_id
    assert config2.tools == config.tools
```

### Testing with Registry

```python
from agent_c_api.api.v2.models.registry import get_model_by_name

def test_model_registry():
    # Get model by name
    model_class = get_model_by_name("AgentConfig")
    assert model_class is not None
    
    # Create instance of dynamically retrieved model
    instance = model_class(
        model_id="gpt-4",
        persona_id="researcher"
    )
    assert instance.model_id == "gpt-4"
```