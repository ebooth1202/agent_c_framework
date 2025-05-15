# API v2 Model Organization Guide

## Overview

This guide provides comprehensive documentation on the organization of Pydantic models in the Agent C API v2. It covers model categories, naming conventions, relationships, and best practices for working with models.

## Model Categories

Models in the API v2 are organized into the following categories:

### 1. Response Models (`response_models.py`)

Common response structures used across the API:

- `APIStatus`: Standard API response status
- `APIResponse`: Standard API response wrapper
- `PaginationMeta`: Pagination metadata
- `PaginatedResponse`: Paginated response wrapper

### 2. Session Models (`session_models.py`)

Models related to session management and agent configuration:

- `SessionCreate`: Parameters for creating a new session
- `SessionSummary`: Basic session info for listings
- `SessionDetail`: Comprehensive session information
- `SessionUpdate`: Parameters for updating session properties
- `SessionListResponse`: Paginated response for session listing
- `AgentConfig`: Detailed agent configuration information
- `AgentUpdate`: Parameters for updating agent configuration
- `AgentUpdateResponse`: Response for agent configuration updates
- `SessionCreateResponse`: Response for session creation

### 3. Agent Models (`agent_models.py`)

Models related to agent capabilities and LLM models:

- `ModelParameter`: LLM model parameter definition
- `ModelInfo`: Information about an LLM model
- `PersonaInfo`: Information about a persona

**Note**: `AgentConfig` and `AgentUpdate` are defined in `session_models.py` but re-exported in `agent_models.py`.

### 4. Chat Models (`chat_models.py`)

Models for chat interactions and messages:

- `FileBlock`: Placeholder for file content blocks
- `ChatMessageContent`: Content of a chat message
- `ChatMessage`: A message in a chat conversation
- `ChatRequest`: Request to send a chat message
- `ChatResponse`: Response containing a chat message
- `ChatEventType`: Enum of event types during chat interaction

### 5. File Models (`file_models.py`)

Models for file handling and uploads:

- `FileMeta`: Metadata about an uploaded file
- `FileUploadResponse`: Response after file upload

### 6. History Models (`history_models.py`)

Models for history and session replay:

- `HistorySummary`: Summary of a recorded session history
- `HistoryDetail`: Detailed information about a session history
- `PaginationParams`: Parameters for pagination
- `HistoryListResponse`: Response for listing session histories
- `EventFilter`: Parameters for filtering history events
- `StoredEvent`: Wrapper around core event models
- `ReplayStatus`: Status of a session replay
- `ReplayControl`: Parameters for controlling replay

### 7. Tool Models (`tool_models.py`)

Models for tool definitions and interactions:

- `ToolParameter`: Tool parameter definition
- `ToolInfo`: Information about a tool
- `ToolCategory`: A category of tools
- `ToolsList`: Comprehensive list of available tools
- `SessionTools`: Tools currently enabled in a session
- `ToolsUpdate`: Parameters for updating session tools
- `ToolCall`: A call to a tool
- `ToolResult`: Result of a tool call

### 8. Debug Models (`debug_models.py`)

Models for debugging and diagnostics:

- `MessagePreview`: Preview of a chat message
- `SessionManagerDebug`: Debug info about session manager
- `ChatSessionDebug`: Debug info about chat session
- `MessagesDebug`: Debug info about messages
- `ToolChestDebug`: Debug info about tool chest
- `ChatLogDebug`: Debug info about chat log
- `SessionDebugInfo`: Comprehensive debug info
- `AgentBridgeParams`: Parameters for agent bridge
- `InternalAgentParams`: Parameters for internal agent
- `AgentDebugInfo`: Debug info about an agent

## Model Registry

All models are registered in the `registry.py` module, which serves as a single source of truth for all models in the API v2. The registry provides functions for accessing models by name or domain.

```python
from agent_c_api.api.v2.models import get_model_by_name, list_models_by_domain

# Get a specific model class
model_class = get_model_by_name("SessionDetail")

# List all models in a domain
session_models = list_models_by_domain("session")
```

## Model Relationships

### Core Relationships

1. **Session ↔ Agent**
   - `SessionDetail` contains agent configuration fields
   - `AgentConfig` defines the agent configuration within a session
   - `AgentUpdate` used to modify agent configuration in a session

2. **Agent ↔ Persona/Model**
   - `AgentConfig.model_id` references a `ModelInfo.id`
   - `AgentConfig.persona_id` references a `PersonaInfo.id`

3. **Session ↔ History**
   - `HistorySummary` and `HistoryDetail` reference sessions
   - `StoredEvent` contains events from a session

4. **Chat ↔ Tools**
   - `ChatMessage` may contain tool calls
   - `ToolCall` and `ToolResult` are used within chat messages

## Import Patterns

### Recommended Import Patterns

1. **Direct Imports (Preferred)**

   Import models directly from their source module:

   ```python
   from agent_c_api.api.v2.models.session_models import SessionDetail, AgentConfig
   ```

2. **Package-Level Imports**

   Import models from the package level (uses explicit imports under the hood):

   ```python
   from agent_c_api.api.v2.models import SessionDetail, AgentConfig
   ```

3. **Domain Group Imports**

   Import groups of related models using the domain groups:

   ```python
   from agent_c_api.api.v2.models import session_models
   
   # Then use session_models.SessionDetail, etc.
   ```

### Special Cases

**AgentConfig and AgentUpdate**: These models are defined in `session_models.py` but also re-exported in `agent_models.py` for backward compatibility. Always import them from `session_models.py`:

```python
# CORRECT
from agent_c_api.api.v2.models.session_models import AgentConfig, AgentUpdate

# AVOID (though it works due to re-exports)
from agent_c_api.api.v2.models.agent_models import AgentConfig, AgentUpdate
```

## Model Design Patterns

### 1. Request/Response Pattern

Many endpoints follow a request/response pattern:

```python
# Request model
class SessionCreate(BaseModel):
    # fields for creating a session

# Response model
class SessionCreateResponse(BaseModel):
    # fields for the response
```

### 2. Detail/Summary Pattern

Models often come in summary and detail versions:

```python
# Summary (lightweight, for listings)
class SessionSummary(BaseModel):
    # basic fields

# Detail (comprehensive, for specific item)
class SessionDetail(SessionSummary):
    # additional detailed fields
```

### 3. Update Pattern

Update models use optional fields for partial updates:

```python
class AgentUpdate(BaseModel):
    # All fields are optional
    temperature: Optional[float] = Field(None, ...)
    # other optional fields
```

## Best Practices

### Creating New Models

1. **Place in the appropriate file** based on the domain
2. **Use clear, descriptive names** following the existing patterns
3. **Add comprehensive docstrings** explaining purpose and relationships
4. **Include Field validators** with appropriate constraints
5. **Add the model to the registry** by updating imports in `registry.py`

### Extending Existing Models

1. **Use inheritance** for models that extend others
2. **Document the inheritance relationship** in docstrings
3. **Consider composition** instead of inheritance when appropriate

### Avoiding Duplication

1. **Check the registry** before creating a new model
2. **Use re-exports** if a model needs to be available in multiple contexts
3. **Run the pre-commit hook** to check for duplicates

```shell
python tools/hooks/check_model_duplication.py
```

## Schema Documentation

API schema documentation is automatically generated from the model definitions. To ensure accurate documentation:

1. **Use meaningful Field descriptions**
2. **Include examples** in model_config/json_schema_extra
3. **Document constraints** like min/max values

Example:

```python
class ModelParameter(BaseModel):
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    type: str = Field(..., description="Parameter type (string, int, float, boolean)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "temperature",
                "value": 0.7,
                "type": "float"
            }
        }
    )
```

## Conclusion

Following these guidelines will help maintain a clean, well-organized set of models for the API v2. The model organization is designed to promote maintainability, clarity, and consistency across the codebase.