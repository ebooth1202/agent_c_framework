from fastapi import Request
from typing import Annotated
from fastapi import Depends

from agent_c_api.api.v2.config.services import ConfigService

# Provider function for ConfigService - modified to always use the same instance
_config_service_instance = None

def get_config_service(request: Request = None) -> ConfigService:
    """
    Dependency provider for ConfigService.
    
    Args:
        request: The FastAPI request object (optional)
        
    Returns:
        ConfigService: Initialized service
    """
    global _config_service_instance
    if _config_service_instance is None:
        _config_service_instance = ConfigService()
    return _config_service_instance

# Type alias for use in route functions
ConfigServiceDep = Annotated[ConfigService, Depends(get_config_service)]