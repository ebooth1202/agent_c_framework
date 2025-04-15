"""MCP Server implementation for Agent C.

This module provides the MCPServer class which represents a connection to an MCP server.
It handles communication, lifecycle management, and tool discovery.
"""

import asyncio
import json
import logging
import os
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPServer:
    """Represents a connection to an MCP server.
    
    Manages the lifecycle of an MCP server connection including startup,
    tool discovery, and execution of tool calls.
    """
    
    def __init__(self, server_id: str, config: Dict[str, Any]):
        """Initialize an MCP server connection.
        
        Args:
            server_id: Unique identifier for this server
            config: Configuration dictionary with:
                - command: Command to run the server
                - args: List of command line arguments
                - env: Environment variables for server
        """
        self.server_id = server_id
        self.config = config
        self.session: Optional[ClientSession] = None
        self.tools: Dict[str, Any] = {}
        self.resources: Dict[str, Any] = {}
        self.prompts: Dict[str, Any] = {}
        self.connected = False
        self.logger = logging.getLogger(f"agent_c.mcp.{server_id}")
        self.exit_stack = AsyncExitStack()
        self._cleanup_lock = asyncio.Lock()
    
    async def connect(self, max_retries=3, retry_delay=1.0) -> bool:
        """Establish connection to the MCP server with retries.
        
        Args:
            max_retries: Maximum number of connection attempts (default: 3)
            retry_delay: Delay between retry attempts in seconds (default: 1.0)
            
        Returns:
            True if successful, False otherwise.
        """
        for attempt in range(max_retries):
            try:
                # Get the command and create server parameters
                command = self.config["command"]
                server_params = StdioServerParameters(
                    command=command,
                    args=self.config.get("args", []),
                    env=self.config.get("env")
                )
                
                # Establish connection to the server
                self.logger.info(f"Connection attempt {attempt+1}/{max_retries} to MCP server {self.server_id}")
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                read, write = stdio_transport
                
                # Create session
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                
                # Initialize session
                await self.session.initialize()
                self.connected = True
                
                # Discover tools
                await self.discover_tools()
                
                self.logger.info(f"Successfully connected to MCP server {self.server_id}")
                return True
            except ConnectionError as e:
                self.logger.warning(f"Connection attempt {attempt+1}/{max_retries} failed (ConnectionError): {e}")
            except asyncio.TimeoutError:
                self.logger.warning(f"Connection attempt {attempt+1}/{max_retries} timed out")
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt+1}/{max_retries} failed: {e}")
            
            # Clean up from failed attempt
            await self.disconnect()
            
            # If we still have retries left, wait before trying again
            if attempt < max_retries - 1:
                self.logger.info(f"Retrying connection in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
        
        self.logger.error(f"Failed to connect to MCP server {self.server_id} after {max_retries} attempts")
        return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the MCP server.
        
        Returns:
            True if successful, False otherwise.
        """
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.connected = False
                self.logger.info(f"Disconnected from MCP server {self.server_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error disconnecting from MCP server {self.server_id}: {e}")
                return False
    
    async def discover_tools(self) -> Dict[str, Any]:
        """Discover available tools from the MCP server.
        
        Returns:
            A dictionary of tool definitions mapped by tool name.
        
        Raises:
            RuntimeError: If the server is not connected.
        """
        if not self.connected or not self.session:
            raise RuntimeError(f"Server {self.server_id} is not connected")
        
        try:
            tools_response = await self.session.list_tools()
            tools = {}
            
            # Extract tools from the response
            for item in tools_response:
                if isinstance(item, tuple) and item[0] == "tools":
                    for tool in item[1]:
                        tools[tool.name] = {
                            "name": tool.name,
                            "description": tool.description,
                            "schema": tool.inputSchema
                        }
            
            self.tools = tools
            self.logger.info(f"Discovered {len(tools)} tools from server {self.server_id}")
            return tools
        except Exception as e:
            self.logger.error(f"Error discovering tools from server {self.server_id}: {e}")
            return {}
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The result from the tool execution formatted as a string
        
        Raises:
            RuntimeError: If the server is not connected
            ValueError: If the tool does not exist
        """
        if not self.connected or not self.session:
            raise RuntimeError(f"Server {self.server_id} is not connected")
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' does not exist on server {self.server_id}")
        
        try:
            self.logger.info(f"Calling tool '{tool_name}' on server {self.server_id} with arguments: {arguments}")
            result = await self.session.call_tool(tool_name, arguments)
            self.logger.debug(f"Raw result from tool '{tool_name}': {result}")
            
            # Process the result to ensure it's in a format suitable for Agent C
            formatted_result = self._format_tool_result(result)
            self.logger.info(f"Tool '{tool_name}' execution completed successfully")
            return formatted_result
        except Exception as e:
            self.logger.error(f"Error calling tool '{tool_name}' on server {self.server_id}: {e}")
            raise
    
    def _format_tool_result(self, result: Any) -> str:
        """Format a tool result for Agent C consumption.
        
        Args:
            result: The raw result from the MCP tool
            
        Returns:
            A string representation of the result suitable for Agent C
        """
        # Handle different result types
        if result is None:
            return "Operation completed successfully with no output."
        
        # If result is already a string, return it directly
        if isinstance(result, str):
            return result
        
        # If result is a simple type (int, float, bool), convert to string
        if isinstance(result, (int, float, bool)):
            return str(result)
        
        # If result is a list or dict, convert to pretty JSON string
        try:
            return json.dumps(result, indent=2, ensure_ascii=False)
        except TypeError:
            # If JSON serialization fails, use string representation
            return str(result)