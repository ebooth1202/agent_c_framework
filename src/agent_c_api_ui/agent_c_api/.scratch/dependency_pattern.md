# FastAPI Dependency Injection Pattern

This document outlines the standardized pattern for dependency injection in the Agent C API v2 structure.

## Service Dependency Pattern

### 1. Dependencies Module

Core dependencies should be defined in `api/dependencies.py`:

```python
from fastapi import Request

def get_agent_manager(request: Request) -> UItoAgentBridgeManager:
    return request.app.state.agent_manager
```

### 2. Service Provider Functions

Service provider functions should:
- Accept a `request: Request` parameter 
- Pass it to any dependencies they use
- Return the constructed service

```python
def get_my_service(request: Request):
    """Dependency to get the service
    
    Args:
        request: The FastAPI request object
        
    Returns:
        MyService: Initialized service
    """
    agent_manager = get_agent_manager(request)
    return MyService(agent_manager=agent_manager)
```

### 3. Service Class Initialization

Service classes should:
- Accept dependencies as constructor parameters
- NOT use `Depends()` directly in constructor parameters

```python
class MyService:
    def __init__(self, agent_manager: UItoAgentBridgeManager):
        self.agent_manager = agent_manager
        # other initialization
```

### 4. Router Endpoint Dependencies

Router endpoints should use the service provider functions with `Depends()`:

```python
@router.get("/endpoint")
async def my_endpoint(
    service: MyService = Depends(get_my_service)
):
    # Use the service
    return await service.do_something()
```

## Troubleshooting

Common issues to check when you encounter dependency errors:

1. Ensure the service provider function accepts a `request: Request` parameter
2. Ensure the service provider function passes the request to any dependencies it uses
3. Ensure the service class doesn't use `Depends()` directly in its constructor

## Why This Pattern?

This pattern ensures that dependencies are properly resolved through the entire chain. When a service depends on another service or a core dependency like the agent manager, the request context must be passed through each level to ensure proper resolution.

The pattern also makes testing easier, as services can be instantiated directly with mock dependencies.