from fastapi import Request
from typing import Annotated
from fastapi import Depends

from agent_c_api.api.v2.config.services import ConfigService

# Provider function for ConfigService
def get_config_service(request: Request) -> ConfigService:
    """
    Dependency provider for ConfigService.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        ConfigService: Initialized service
    """
    return ConfigService()

# Type alias for use in route functions
ConfigServiceDep = Annotated[ConfigService, Depends(get_config_service)]