"""MCP Server implementation for Agent C.

This module provides the MCPServer class which represents a connection to an MCP server.
It handles communication, lifecycle management, and tool discovery for multiple transport types.
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union, AsyncContextManager, AsyncGenerator, Protocol
from urllib.parse import urlparse

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client


class TransportType(Enum):
    """Types of supported MCP transports."""
    STDIO = auto()
    SSE = auto()
    

class MCPTransport(Protocol):
    """Protocol for MCP transport implementations."""
    
    @abstractmethod
    async def connect(self, exit_stack: AsyncExitStack) -> Tuple[Any, Any]:
        """Connect to the MCP server and return read/write streams.
        
        Args:
            exit_stack: AsyncExitStack for resource management
            
        Returns:
            Tuple of (read_stream, write_stream)
        """
        ...


class StdioTransport:
    """STDIO transport for MCP."""
    
    def __init__(self, server_params: StdioServerParameters):
        """Initialize STDIO transport.
        
        Args:
            server_params: STDIO server parameters
        """
        self.server_params = server_params
    
    async def connect(self, exit_stack: AsyncExitStack) -> Tuple[Any, Any]:
        """Connect to the MCP server using STDIO.
        
        Args:
            exit_stack: AsyncExitStack for resource management
            
        Returns:
            Tuple of (read_stream, write_stream)
        """
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )
        return stdio_transport


class SSETransport:
    """Server-Sent Events (SSE) transport for MCP."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, Any]] = None, 
                 timeout: float = 5.0, sse_read_timeout: float = 300.0):
        """Initialize SSE transport.
        
        Args:
            url: The URL to connect to
            headers: Optional HTTP headers to include
            timeout: HTTP timeout in seconds
            sse_read_timeout: SSE read timeout in seconds
        """
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout
        self.sse_read_timeout = sse_read_timeout
    
    async def connect(self, exit_stack: AsyncExitStack) -> Tuple[Any, Any]:
        """Connect to the MCP server using SSE.
        
        Args:
            exit_stack: AsyncExitStack for resource management
            
        Returns:
            Tuple of (read_stream, write_stream)
        """
        sse_transport = await exit_stack.enter_async_context(
            sse_client(
                self.url,
                headers=self.headers,
                timeout=self.timeout,
                sse_read_timeout=self.sse_read_timeout
            )
        )
        return sse_transport


class MCPServer:
    """Represents a connection to an MCP server.
    
    Manages the lifecycle of an MCP server connection including startup,
    tool discovery, and execution of tool calls. Supports multiple transport types.
    """
    
    def __init__(self, server_id: str, config: Dict[str, Any]):
        """Initialize an MCP server connection.
        
        Args:
            server_id: Unique identifier for this server
            config: Configuration dictionary with:
                - transport_type: Type of transport ("stdio" or "sse")
                For STDIO:
                  - command: Command to run the server
                  - args: List of command line arguments
                  - env: Environment variables for server
                For SSE:
                  - url: The SSE endpoint URL
                  - headers: Optional HTTP headers
                  - timeout: Optional HTTP timeout
                  - sse_read_timeout: Optional SSE read timeout
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
        
        # Determine transport type
        transport_type = self.config.get("transport_type", "stdio").lower()
        if transport_type == "stdio":
            self.transport_type = TransportType.STDIO
        elif transport_type == "sse":
            self.transport_type = TransportType.SSE
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
        
        # Create the appropriate transport
        self._transport = self._create_transport()
    
    def _create_transport(self) -> MCPTransport:
        """Create the appropriate transport based on configuration.
        
        Returns:
            An instance of the appropriate transport class
        
        Raises:
            ValueError: If transport configuration is invalid
        """
        if self.transport_type == TransportType.STDIO:
            if "command" not in self.config:
                raise ValueError("STDIO transport requires 'command' in configuration")
            
            server_params = StdioServerParameters(
                command=self.config["command"],
                args=self.config.get("args", []),
                env=self.config.get("env")
            )
            return StdioTransport(server_params)
        
        elif self.transport_type == TransportType.SSE:
            if "url" not in self.config:
                raise ValueError("SSE transport requires 'url' in configuration")
            
            url = self.config["url"]
            headers = self.config.get("headers")
            timeout = self.config.get("timeout", 5.0)
            sse_read_timeout = self.config.get("sse_read_timeout", 300.0)
            
            return SSETransport(url, headers, timeout, sse_read_timeout)
        
        else:
            raise ValueError(f"Unsupported transport type: {self.transport_type}")
    
    async def connect(self, max_retries=3, retry_delay=1.0) -> bool:
        """Establish connection to the MCP server with retries.
        
        Args:
            max_retries: Maximum number of connection attempts (default: 3)
            retry_delay: Delay between retry attempts in seconds (default: 1.0)
            
        Returns:
            True if successful, False otherwise.
        """
        transport_name = self.transport_type.name
        for attempt in range(max_retries):
            try:
                # Log connection attempt
                self.logger.info(
                    f"Connection attempt {attempt+1}/{max_retries} to MCP server {self.server_id} "
                    f"using {transport_name} transport"
                )
                
                # Connect to the server using the appropriate transport
                read, write = await self._transport.connect(self.exit_stack)
                
                # Create session
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                
                # Initialize session
                await self.session.initialize()
                self.connected = True
                
                # Discover tools
                await self.discover_tools()
                await self.discover_resources()
                await self.discover_prompts()
                
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
    
    async def discover_resources(self) -> Dict[str, Any]:
        """Discover available resources from the MCP server.
        
        Returns:
            A dictionary of resource definitions mapped by resource URI.
        
        Raises:
            RuntimeError: If the server is not connected.
        """
        if not self.connected or not self.session:
            raise RuntimeError(f"Server {self.server_id} is not connected")
        
        try:
            resources_response = await self.session.list_resources()
            resources = {}
            
            # Extract resources from the response
            for item in resources_response:
                if isinstance(item, tuple) and item[0] == "resources":
                    for resource in item[1]:
                        resources[str(resource.uri)] = {
                            "uri": str(resource.uri),
                            "mimeType": resource.mimeType,
                        }
            
            self.resources = resources
            self.logger.info(f"Discovered {len(resources)} resources from server {self.server_id}")
            return resources
        except Exception as e:
            self.logger.error(f"Error discovering resources from server {self.server_id}: {e}")
            return {}
    
    async def discover_prompts(self) -> Dict[str, Any]:
        """Discover available prompts from the MCP server.
        
        Returns:
            A dictionary of prompt definitions mapped by prompt name.
        
        Raises:
            RuntimeError: If the server is not connected.
        """
        if not self.connected or not self.session:
            raise RuntimeError(f"Server {self.server_id} is not connected")
        
        try:
            prompts_response = await self.session.list_prompts()
            prompts = {}
            
            # Extract prompts from the response
            for item in prompts_response:
                if isinstance(item, tuple) and item[0] == "prompts":
                    for prompt in item[1]:
                        prompts[prompt.name] = {
                            "name": prompt.name,
                            "description": prompt.description,
                            "parameters": prompt.parameters,
                        }
            
            self.prompts = prompts
            self.logger.info(f"Discovered {len(prompts)} prompts from server {self.server_id}")
            return prompts
        except Exception as e:
            self.logger.error(f"Error discovering prompts from server {self.server_id}: {e}")
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
            await self.connect()

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
    
    async def read_resource(self, resource_uri: str) -> Tuple[str, str]:
        """Read content from a resource on the MCP server.
        
        Args:
            resource_uri: URI of the resource to read
            
        Returns:
            Tuple of (content, mime_type)
        
        Raises:
            RuntimeError: If the server is not connected
            ValueError: If the resource does not exist
        """
        if not self.connected or not self.session:
            raise RuntimeError(f"Server {self.server_id} is not connected")
        
        if resource_uri not in self.resources:
            raise ValueError(f"Resource '{resource_uri}' does not exist on server {self.server_id}")
        
        try:
            self.logger.info(f"Reading resource '{resource_uri}' from server {self.server_id}")
            result = await self.session.read_resource(resource_uri)
            
            content = result.content
            mime_type = result.mimeType
            
            self.logger.info(f"Resource '{resource_uri}' read successfully")
            return content, mime_type
        except Exception as e:
            self.logger.error(f"Error reading resource '{resource_uri}' from server {self.server_id}: {e}")
            raise
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, str] = None) -> str:
        """Get a prompt from the MCP server with optional arguments.
        
        Args:
            prompt_name: Name of the prompt to get
            arguments: Optional arguments to pass to the prompt
            
        Returns:
            The prompt text
        
        Raises:
            RuntimeError: If the server is not connected
            ValueError: If the prompt does not exist
        """
        if not self.connected or not self.session:
            raise RuntimeError(f"Server {self.server_id} is not connected")
        
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' does not exist on server {self.server_id}")
        
        try:
            self.logger.info(f"Getting prompt '{prompt_name}' from server {self.server_id}")
            result = await self.session.get_prompt(prompt_name, arguments or {})
            
            prompt_text = result.prompt
            
            self.logger.info(f"Prompt '{prompt_name}' retrieved successfully")
            return prompt_text
        except Exception as e:
            self.logger.error(f"Error getting prompt '{prompt_name}' from server {self.server_id}: {e}")
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