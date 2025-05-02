# Agent C API V2 - First Implementation Step

## Overview

This document outlines the specific changes we'll make to begin the v2 API implementation, focusing on establishing the project structure and foundation. This is the first step in our phased implementation plan.

## Project Structure Changes

### 1. Create v2 API Base Router

**File**: `/api/v2/__init__.py`

```python
# src/agent_c_api/api/v2/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/v2")

# These routers will be included as they're implemented
# from .config import router as config_router
# from .sessions import router as sessions_router
# from .history import router as history_router
# from .debug import router as debug_router

# router.include_router(config_router)
# router.include_router(sessions_router)
# router.include_router(history_router)
# router.include_router(debug_router)
```

### 2. Create Resource Directories

Create the following directory structure to organize the v2 API resources:

```
src/agent_c_api/api/v2/
  __init__.py
  config/
    __init__.py
    models.py
    personas.py
    tools.py
    system.py
  sessions/
    __init__.py
    sessions.py
    agent.py
    tools.py
    chat.py
    files.py
  history/
    __init__.py
    history.py
    events.py
    replay.py
  debug/
    __init__.py
    debug.py
  models/
    __init__.py
    session_models.py
    agent_models.py
    tool_models.py
    chat_models.py
    file_models.py
    history_models.py
    response_models.py
  utils/
    __init__.py
    pagination.py
    error_handling.py
    validation.py
```

### 3. Create Base Configuration Routers

**File**: `/api/v2/config/__init__.py`

```python
# src/agent_c_api/api/v2/config/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/config")

# These routers will be included as they're implemented
# from .models import router as models_router
# from .personas import router as personas_router
# from .tools import router as tools_router
# from .system import router as system_router

# router.include_router(models_router)
# router.include_router(personas_router)
# router.include_router(tools_router)
# router.include_router(system_router)
```

**File**: `/api/v2/sessions/__init__.py`

```python
# src/agent_c_api/api/v2/sessions/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/sessions")

# These routers will be included as they're implemented
# from .sessions import router as sessions_router
# from .agent import router as agent_router
# from .tools import router as tools_router
# from .chat import router as chat_router
# from .files import router as files_router

# router.include_router(sessions_router)
# router.include_router(agent_router)
# router.include_router(tools_router)
# router.include_router(chat_router)
# router.include_router(files_router)
```

**File**: `/api/v2/history/__init__.py`

```python
# src/agent_c_api/api/v2/history/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/history")

# These routers will be included as they're implemented
# from .history import router as history_router
# from .events import router as events_router
# from .replay import router as replay_router

# router.include_router(history_router)
# router.include_router(events_router)
# router.include_router(replay_router)
```

**File**: `/api/v2/debug/__init__.py`

```python
# src/agent_c_api/api/v2/debug/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/debug")

# These will be included as they're implemented
# from .debug import router as debug_router

# router.include_router(debug_router)
```

### 4. Set Up Base Models Structure

**File**: `/api/v2/models/__init__.py`

```python
# src/agent_c_api/api/v2/models/__init__.py
# Export all models for convenient imports
from .response_models import *
from .session_models import *
from .agent_models import *
from .tool_models import *
from .chat_models import *
from .file_models import *
from .history_models import *
```

**File**: `/api/v2/models/response_models.py`

```python
# src/agent_c_api/api/v2/models/response_models.py
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIStatus(BaseModel):
    """Standard API response status"""
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Optional message about the request")
    error_code: Optional[str] = Field(None, description="Error code if applicable")

class APIResponse(Generic[T], BaseModel):
    """Standard API response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status information")
    data: Optional[T] = Field(None, description="Response data")

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

class PaginatedResponse(Generic[T], BaseModel):
    """Paginated response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status information")
    data: List[T] = Field(default_factory=list, description="Paginated items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
```

### 5. Update Main API Router to Include v2

**File**: `src/agent_c_api/api/__init__.py`

Update to include the v2 router:

```python
# src/agent_c_api/api/__init__.py
from fastapi import APIRouter
from .v1 import router as v1_router
from .v2 import router as v2_router  # Add this import

router = APIRouter(prefix="/api")
router.include_router(v1_router)
router.include_router(v2_router)  # Add this line
```

### 6. Create Testing Directory Structure

Create the following test directory structure for v2 API tests:

```
src/agent_c_api/tests/v2/
  __init__.py
  conftest.py
  test_api_structure.py
  config/
    __init__.py
    test_models.py
    test_personas.py
    test_tools.py
    test_system.py
  sessions/
    __init__.py
    test_sessions.py
    test_agent.py
    test_tools.py
    test_chat.py
    test_files.py
  history/
    __init__.py
    test_history.py
    test_events.py
    test_replay.py
  debug/
    __init__.py
    test_debug.py
  models/
    __init__.py
    test_response_models.py
```

### 7. Create Initial Test for API Structure

**File**: `src/agent_c_api/tests/v2/test_api_structure.py`

```python
# src/agent_c_api/tests/v2/test_api_structure.py
from fastapi.testclient import TestClient
from agent_c_api.main import app

client = TestClient(app)

def test_v2_api_route_exists():
    """Test that the /api/v2 route exists and returns 404 (since no endpoints are implemented yet)"""
    response = client.get("/api/v2")
    # Should be 404 since we haven't implemented any endpoints at the root yet
    assert response.status_code == 404
    
    # Test that the app is working correctly - the docs should be accessible
    response = client.get("/docs")
    assert response.status_code == 200
```

### 8. Create Documentation Template

**File**: `docs/v2_api_documentation.md`

```markdown
# Agent C API v2 Documentation

## Overview

The Agent C API v2 provides a clean, RESTful interface for interacting with Agent C. It's organized around resource types with consistent HTTP methods and status codes.

## API Resources

### Configuration Resources

- `/api/v2/config/models` - Available LLM models
- `/api/v2/config/personas` - Available personas
- `/api/v2/config/tools` - Available tools
- `/api/v2/config/system` - Combined system configuration

### Session Resources

- `/api/v2/sessions` - Chat session management
- `/api/v2/sessions/{session_id}` - Individual session operations
- `/api/v2/sessions/{session_id}/agent` - Agent configuration
- `/api/v2/sessions/{session_id}/tools` - Session tools management
- `/api/v2/sessions/{session_id}/chat` - Chat messaging
- `/api/v2/sessions/{session_id}/files` - File management

### History Resources

- `/api/v2/history` - Session history listing
- `/api/v2/history/{session_id}` - Session history management
- `/api/v2/history/{session_id}/events` - Event access
- `/api/v2/history/{session_id}/stream` - Event streaming
- `/api/v2/history/{session_id}/replay` - Replay controls

### Debug Resources

- `/api/v2/debug/sessions/{session_id}` - Session debugging
- `/api/v2/debug/agent/{session_id}` - Agent state debugging

## Implementation Status

- [ ] Configuration Resources
- [ ] Session Resources
- [ ] History Resources
- [ ] Debug Resources

## Migration from v1

See the migration guide for details on transitioning from v1 to v2 API.
```

## Justification

This initial implementation step lays the foundation for the entire v2 API without disrupting the existing v1 API. We're creating:

1. **Clear Directory Structure**: Organizing code by resource type for maintainability
2. **Router Hierarchy**: Setting up the router structure that will connect all components
3. **Base Models**: Creating response model foundations for consistent API responses
4. **Test Infrastructure**: Setting up the testing structure to ensure quality
5. **Documentation Template**: Beginning the documentation that will grow with the API

All of these changes are non-disruptive to the existing API and create the scaffolding for our continued implementation.

## Next Steps After Approval

Once this foundation is approved and implemented, we'll move to planning the implementation session for the core models and the first set of endpoints (configuration resources) as outlined in our implementation plan.