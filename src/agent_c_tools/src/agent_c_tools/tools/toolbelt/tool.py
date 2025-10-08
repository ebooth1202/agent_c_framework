from typing import TYPE_CHECKING

from agent_c.toolsets import Toolset, json_schema

if TYPE_CHECKING:
    from agent_c_api.core.realtime_bridge import RealtimeBridge

class ToolbeltTools(Toolset):
    """
    Provides your agent with capabilities to equip and remove toolsets.
    """

    def __init__(self, **kwargs):
        """
        Initialize the ToolbeltTools.

        Args:
            **kwargs: Keyword arguments passed to parent Toolset class.
        """
        super().__init__(**kwargs, name='toolbelt')

    @json_schema(
        description="Equip a toolset so it's tools can be used",
        params={
            'toolset_name': {
                'type': 'string',
                'description': 'The name of the toolset to equip',
                'required': True
            }
        }
    )
    async def equip(self, **kwargs) -> str:
        """
       Add a toolset to the agent's available tools via the RealTimeBridge.

        Args:
            toolset_name (str): The name of the toolset to equip.

        Returns:
            str: Success message or error description
        """
        toolset_name = kwargs.get('toolset_name')
        tool_context = kwargs.get('tool_context')

        try:
            if not toolset_name:
                return "ERROR: toolset_name parameter is required"
                
            if not tool_context or 'bridge' not in tool_context:
                return "ERROR: Bridge not available in tool context"

            bridge: 'RealtimeBridge'  = tool_context['bridge']

            equipped = await bridge.add_tool(toolset_name)
            if not equipped:
                return f"ERROR: Failed to equip toolset: {toolset_name}"

            await bridge.send_system_message(f"Agent has equipped {toolset_name} toolset.", severity="info")

            return f"{toolset_name} equipped"
            
        except Exception as e:
            error_msg = f"Failed to equip toolset: {toolset_name} {str(e)}"
            self.logger.error(error_msg)
            return f"ERROR: {error_msg}"

    @json_schema(
        description="Remove a toolset that is no longer needed.",
        params={
            'toolset_name': {
                'type': 'string',
                'description': 'The name of the toolset to remove',
                'required': True
            }
        }
    )
    async def remove(self, **kwargs) -> str:
        """
        Remove a toolset from the agent's available tools via the RealTimeBridge.

        Args:
            toolset_name (str): The name of the toolset to equip.

        Returns:
            str: Success message or error description
        """
        toolset_name = kwargs.get('toolset_name')
        tool_context = kwargs.get('tool_context')
        if not toolset_name:
            return "ERROR: toolset_name parameter is required"

        if not tool_context or 'bridge' not in tool_context:
            return "ERROR: Bridge not available in tool context"

        bridge: 'RealtimeBridge' = tool_context['bridge']

        try:
            removed = await bridge.remove_tool(toolset_name)
            if not removed:
                return f"ERROR: Failed to remove toolset: {toolset_name}"

            await bridge.send_system_message(f"Agent has removed {toolset_name} toolset.", severity="info")

            return f"{toolset_name} removed"

        except Exception as e:
            error_msg = f"Failed to remove toolset: {toolset_name} {str(e)}"
            await bridge.send_system_message(f"Agent has removed {toolset_name} toolset.", severity="error")
            self.logger.error(error_msg)
            return f"ERROR: {error_msg}"

    @json_schema(
        description="Get the list of toolset names",
        params={}
    )
    async def list(self, **kwargs) -> str:
        """
        Get a list of available toolset names.
        """
        try:
            catalog = Toolset.get_client_registry()
            names = [tool.name for tool in catalog]

            return self._yaml_dump({"toolsets": names})

        except Exception as e:
            error_msg = f"Failed to list toolsets: {str(e)}"
            self.logger.error(error_msg)
            return f"ERROR: {error_msg}"

    @json_schema(
        description="Get the details on an available toolset",
        params={
            'toolset_name': {
                'type': 'string',
                'description': 'The name of the toolset to get details for',
                'required': True
            }
        }
    )
    async def details(self, **kwargs) -> str:
        """
        Get a list of available toolset names.
        """
        toolset_name = kwargs.get('toolset_name')
        if not toolset_name:
            return "ERROR: toolset_name parameter is required"

        try:
            catalog = Toolset.get_client_registry()
            if toolset_name:
                catalog = [tool for tool in catalog if tool.name == toolset_name]

            if not catalog:
                return f"ERROR: No toolset found with name: {toolset_name}"

            return self._yaml_dump(catalog)


        except Exception as e:
            error_msg = f"Failed to get details for toolset {toolset_name}: {str(e)}"
            self.logger.error(error_msg)
            return f"ERROR: {error_msg}"

# Register the toolset
Toolset.register(ToolbeltTools)