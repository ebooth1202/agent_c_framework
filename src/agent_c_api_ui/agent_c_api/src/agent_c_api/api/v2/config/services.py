from typing import Optional, TYPE_CHECKING
from fastapi_cache.decorator import cache
from sympy import false

from agent_c.config.agent_config_loader import AgentConfigLoader

from agent_c.toolsets.tool_set import Toolset
from agent_c_api.config.config_loader import MODELS_CONFIG
from agent_c_api.api.v2.models.config_models import (
    ModelInfo, ToolInfo, ModelParameter,
    ModelsResponse, AgentConfigsResponse, ToolsResponse, SystemConfigResponse
)

if TYPE_CHECKING:
    from agent_c.models.agent_config import AgentConfiguration, CurrentAgentConfiguration



class ConfigService:
    """Service for retrieving configuration data from existing sources"""
    def __init__(self):
        self.agent_config_loader: AgentConfigLoader = AgentConfigLoader()

    @cache(expire=300)  # Cache for 5 minutes
    async def get_models(self) -> ModelsResponse:
        """
        Get available models using the existing configuration mechanism
        """
        # Using the same approach as in v1/models.py
        model_list = []
        
        # Process models in the same format as v1 API
        if not MODELS_CONFIG:
            return ModelsResponse(models=[])
            
        for vendor in MODELS_CONFIG.get("vendors", []):
            vendor_name = vendor.get("vendor")
            for model in vendor.get("models", []):
                # Transform to our v2 model format
                parameters = []
                for param_name, param_data in model.get("parameters", {}).items():
                    parameters.append(ModelParameter(
                        name=param_name,
                        type=param_data.get("type", "string"),
                        description=param_data.get("description", ""),
                        default=param_data.get("default")
                    ))
                
                # Transform capabilities from dict to list if needed
                capabilities = []
                if isinstance(model.get("capabilities", {}), dict):
                    capabilities = [key for key, value in model.get("capabilities", {}).items() if value]
                elif isinstance(model.get("capabilities", []), list):
                    capabilities = model.get("capabilities", [])
                
                # Transform allowed_inputs from dict to list if needed
                allowed_inputs = []
                if isinstance(model.get("allowed_inputs", {}), dict):
                    allowed_inputs = [key for key, value in model.get("allowed_inputs", {}).items() if value]
                elif isinstance(model.get("allowed_inputs", []), list):
                    allowed_inputs = model.get("allowed_inputs", [])
                
                model_info = ModelInfo(
                    id=model["id"],
                    name=model.get("ui_name", model["id"]),
                    provider=vendor_name,
                    description=model.get("description", ""),
                    capabilities=capabilities,
                    parameters=parameters,
                    allowed_inputs=allowed_inputs
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
    async def get_agent_configs(self) -> AgentConfigsResponse:
        """
        Get available agent configurations
        """
        return AgentConfigsResponse(agents=list(self.agent_config_loader.catalog.values()))

    @cache(expire=300)  # Cache for 5 minutes
    async def get_agent_config(self, agent_key: str) -> Optional['CurrentAgentConfiguration']:
        """
        Get a specific agent by ID
        """
        if agent_key not in self.agent_config_loader.catalog:
            return None

        return self.agent_config_loader.catalog[agent_key]
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_personas(self) -> AgentConfigsResponse:
        """
        Get available personas (agents with 'domo' category) using the existing file-based mechanism
        """
        # Filter agents that have 'domo' in their category (similar to v1 personas endpoint)
        domo_agents = []
        for agent_config in self.agent_config_loader.catalog.values():
            if "domo" in agent_config.category:
                domo_agents.append(agent_config)
        
        return AgentConfigsResponse(agents=domo_agents)
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_persona(self, persona_id: str) -> Optional[PersonaInfo]:
        """
        Get a specific persona by ID, converted to PersonaInfo format
        """
        if persona_id not in self.agent_config_loader.catalog:
            return None
        
        agent_config = self.agent_config_loader.catalog[persona_id]
        
        # Only return if this agent has 'domo' in category (is a persona)
        if "domo" not in agent_config.category:
            return None
        
        # Convert AgentConfiguration to PersonaInfo
        return PersonaInfo(
            id=agent_config.key,
            name=agent_config.name,
            description=agent_config.agent_description,
            file_path=f"{agent_config.key}.yaml",
            content=agent_config.persona[:1000] if agent_config.persona else None  # Truncate for display
        )
    
    @cache(expire=300)  # Cache for 5 minutes
    async def get_tools(self) -> ToolsResponse:
        """
        Get available tools using the existing tool discovery mechanism
        """
        # Using the same approach as in v1/tools.py
        tool_list = []
        categories = set()
        essential_tools = []
        
        # Categories mapping similar to v1 implementation
        category_mapping = {
            'agent_c_tools': 'Core Tools'
        }
        
        # Get all tools from the Toolset registry
        for tool_class in Toolset.tool_registry:
            # Determine category based on module name
            category = "General"
            for module_prefix, category_name in category_mapping.items():
                if tool_class.__module__.startswith(module_prefix):
                    category = category_name
                    break
                    
            categories.add(category)
            
            # Check if tool is essential
            is_essential = false
            
            # Get parameters from tool class (simplified approach)
            parameters = []
            # For now, we don't have easy access to parameter info
            # This would require inspecting the tool class more thoroughly
            
            # Create tool info
            tool_info = ToolInfo(
                id=tool_class.__name__,
                name=tool_class.__name__,
                description=tool_class.__doc__ or "",
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
        
        # Convert AgentConfiguration objects to PersonaInfo objects
        persona_infos = []
        for agent_config in personas_response.agents:
            persona_info = PersonaInfo(
                id=agent_config.key,
                name=agent_config.name,
                description=agent_config.agent_description,
                file_path=f"{agent_config.key}.yaml",
                content=agent_config.persona[:1000] if agent_config.persona else None  # Truncate for display
            )
            persona_infos.append(persona_info)
        
        return SystemConfigResponse(
            models=models_response.models,
            personas=persona_infos,
            tools=tools_response.tools,
            tool_categories=tools_response.categories,
            essential_tools=tools_response.essential_tools
        )