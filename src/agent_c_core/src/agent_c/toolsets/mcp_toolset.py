"""MCP Toolset implementation for Agent C.

This module provides the MCPToolset class which represents tools from an MCP server
as a standard Agent C toolset.
"""

import inspect
import json
import logging
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Type, Union

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.mcp_server import MCPServer


class MCPToolset(Toolset):
    """A toolset representing tools from an MCP server.
    
    Dynamically creates methods for MCP tools to be used by Agent C.
    """
    
    def __init__(self, server: MCPServer, **kwargs):
        """Initialize the MCPToolset.
        
        Args:
            server: The MCPServer this toolset represents
            **kwargs: Additional arguments for the Toolset base class
        """
        # Initialize with a name based on the server ID
        name = kwargs.pop("name", f"mcp_{server.server_id}")
        super().__init__(name=name, **kwargs)
        
        self.server = server
        self.logger = logging.getLogger(f"agent_c.mcp_toolset.{server.server_id}")
        
        # Create dynamic methods for MCP tools
        self._create_tool_methods()
    
    def _create_tool_methods(self):
        """Dynamically create methods for each tool in the server.
        
        This method creates a Python method for each tool in the MCP server,
        with appropriate docstrings and type hints to work with Agent C.
        """
        for tool_name, tool_info in self.server.tools.items():
            # Create a method that will call the MCP tool
            method = self._create_tool_method(tool_name, tool_info)
            
            # Add the method to the class instance
            method_name = f"mcp_{tool_name.replace('-', '_')}"
            setattr(self, method_name, method)
            
            # Apply json_schema decorator to the method for proper Agent C integration
            # This part is handled by the Toolset class's __init__ method
            self.logger.info(f"Created method {method_name} for MCP tool {tool_name}")
    
    def _create_tool_method(self, tool_name: str, tool_info: Dict[str, Any]) -> Callable:
        """Create a method that calls an MCP tool.
        
        Args:
            tool_name: Name of the MCP tool
            tool_info: Tool information including description and schema
            
        Returns:
            A callable method that will invoke the MCP tool
        """
        # Get tool schema and description
        schema = tool_info.get("schema", {})
        description = tool_info.get("description", f"MCP tool: {tool_name}")
        
        # Generate function signature from the schema
        param_names = []
        param_docs = []
        if "properties" in schema:
            param_names = list(schema["properties"].keys())
            for param_name, param_props in schema["properties"].items():
                param_desc = param_props.get("description", f"Parameter {param_name}")
                param_type = param_props.get("type", "any")
                param_docs.append(f"    {param_name}: {param_desc} ({param_type})")
        
        # Build a proper docstring with parameter descriptions
        full_docstring = f"{description}\n\nArgs:\n{chr(10).join(param_docs)}\n\nReturns:\n    The result from the MCP tool execution"
        
        # Define the actual async method that will call the MCP tool
        async def mcp_tool_method(**kwargs):
            # Remove any kwargs that are not part of the MCP tool's expected parameters
            # This is to accommodate Agent C's method calling convention
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in param_names}
            
            # Log the tool call
            self.logger.info(f"Calling MCP tool '{tool_name}' with arguments: {filtered_kwargs}")
            
            # Call the MCP tool through the server
            try:
                result = await self.server.call_tool(tool_name, filtered_kwargs)
                self.logger.debug(f"Result from MCP tool '{tool_name}': {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error calling MCP tool '{tool_name}': {e}")
                raise RuntimeError(f"Failed to execute MCP tool '{tool_name}': {e}")
        
        # Set docstring and metadata for proper display in schemas
        mcp_tool_method.__doc__ = full_docstring
        mcp_tool_method.__name__ = f"mcp_{tool_name.replace('-', '_')}"
        
        # Set additional metadata for schema generation
        # This gets automatically picked up by Toolset's __init__ for schema generation
        return mcp_tool_method