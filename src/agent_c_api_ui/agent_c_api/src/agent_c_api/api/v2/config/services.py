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
    async def get_models(self) -> ModelsResponse:
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
    async def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get a specific model by ID
        """
        models_response = await self.get_models()
        for model in models_response.models:
            if model.id == model_id:
                return model
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_personas(self) -> PersonasResponse:
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
    async def get_persona(self, persona_id: str) -> Optional[PersonaInfo]:
        """
        Get a specific persona by ID
        """
        personas_response = await self.get_personas()
        for persona in personas_response.personas:
            if persona.id == persona_id:
                return persona
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_tools(self) -> ToolsResponse:
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
    async def get_tool(self, tool_id: str) -> Optional[ToolInfo]:
        """
        Get a specific tool by ID
        """
        tools_response = await self.get_tools()
        for tool in tools_response.tools:
            if tool.id == tool_id:
                return tool
        return None
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_system_config(self) -> SystemConfigResponse:
        """
        Get combined system configuration
        """
        models_response = await self.get_models()
        personas_response = await self.get_personas()
        tools_response = await self.get_tools()
        
        return SystemConfigResponse(
            models=models_response.models,
            personas=personas_response.personas,
            tools=tools_response.tools,
            tool_categories=tools_response.categories,
            essential_tools=tools_response.essential_tools
        )