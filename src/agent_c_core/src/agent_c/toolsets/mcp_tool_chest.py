"""MCP Tool Chest implementation for Agent C.

This module provides the MCPToolChest class which extends the standard ToolChest
to include support for MCP servers and their tools.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import yaml

from agent_c.toolsets.tool_chest import ToolChest
from agent_c.toolsets.mcp_server import MCPServer
from agent_c.toolsets.mcp_toolset import MCPToolset


class MCPToolChest(ToolChest):
    """A tool chest that includes support for MCP servers.
    
    Manages multiple MCP server connections and makes their tools available
    as standard Agent C tools.
    """
    
    def __init__(self, **kwargs):
        """Initialize the MCPToolChest.
        
        Args:
            **kwargs: Arguments to pass to the ToolChest base class
        """
        super().__init__(**kwargs)
        self.mcp_servers: Dict[str, MCPServer] = kwargs.get("mcp_servers", {})
        self.logger = logging.getLogger("agent_c.mcp_tool_chest")
    
    def load_config(self, config_path: str):
        """Load MCP server configurations from a file.
        
        Args:
            config_path: Path to the configuration file (YAML or JSON)
            
        Returns:
            Dict[str, Any]: Loaded configuration
            
        Raises:
            FileNotFoundError: If the config file does not exist
            ValueError: If the config file format is invalid
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Determine file format and load accordingly
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".json":
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        # Process servers configuration
        if "servers" not in config:
            raise ValueError("Invalid configuration: 'servers' key is missing")
        
        # Add each server from the configuration
        for server_id, server_config in config["servers"].items():
            self.add_server(server_id, **server_config)
        
        self.logger.info(f"Loaded {len(config['servers'])} MCP server configurations from {config_path}")
        return config
    
    def add_server(self, server_id: str, **server_config):
        """Add an MCP server programmatically.
        
        Args:
            server_id: Unique identifier for this server
            **server_config: Configuration for the server including:
                - command: Command to run the server
                - args: List of command line arguments
                - env: Environment variables for server
        """
        if server_id in self.mcp_servers:
            self.logger.warning(f"Replacing existing MCP server configuration for {server_id}")
        
        # Create MCPServer instance
        server = MCPServer(server_id, server_config)
        self.mcp_servers[server_id] = server
        self.logger.info(f"Added MCP server configuration for {server_id}")
    
    async def connect_servers(self):
        """Connect to all configured MCP servers.
        
        Returns:
            Dict[str, bool]: Dictionary mapping server IDs to connection success status
        """
        connection_results = {}
        connection_tasks = []
        
        # Create connection tasks for all servers
        for server_id, server in self.mcp_servers.items():
            task = asyncio.create_task(server.connect())
            connection_tasks.append((server_id, task))
        
        # Wait for all connections to complete
        for server_id, task in connection_tasks:
            try:
                success = await task
                connection_results[server_id] = success
                
                # If successfully connected, create a toolset for this server
                if success:
                    toolset = MCPToolset(self.mcp_servers[server_id])
                    self.add_tool_instance(toolset)
                    self.logger.info(f"Added toolset for MCP server {server_id}")
            except Exception as e:
                self.logger.error(f"Error connecting to MCP server {server_id}: {e}")
                connection_results[server_id] = False
        
        return connection_results
    
    async def disconnect_servers(self):
        """Disconnect from all MCP servers.
        
        Returns:
            Dict[str, bool]: Dictionary mapping server IDs to disconnection success status
        """
        disconnection_results = {}
        disconnection_tasks = []
        
        # Create disconnection tasks for all servers
        for server_id, server in self.mcp_servers.items():
            if server.connected:
                task = asyncio.create_task(server.disconnect())
                disconnection_tasks.append((server_id, task))
        
        # Wait for all disconnections to complete
        for server_id, task in disconnection_tasks:
            try:
                success = await task
                disconnection_results[server_id] = success
            except Exception as e:
                self.logger.error(f"Error disconnecting from MCP server {server_id}: {e}")
                disconnection_results[server_id] = False
        
        return disconnection_results
    
    async def init_tools(self, **kwargs):
        """Override of ToolChest.init_tools to also initialize MCP servers.
        
        Args:
            **kwargs: Arguments to pass to the parent class and tools during initialization
        """
        # First init regular tools
        await super().init_tools(**kwargs)
        
        # Then connect and initialize MCP servers
        connection_results = await self.connect_servers()
        
        # Log connection results
        successful = sum(1 for result in connection_results.values() if result)
        failed = sum(1 for result in connection_results.values() if not result)
        self.logger.info(f"Initialized MCP servers and tools: {successful} connected, {failed} failed")
        
        if failed > 0:
            self.logger.warning(f"Some MCP servers failed to connect. Check logs for details.")
        
        return connection_results
    
    async def shutdown(self):
        """Shutdown all MCP servers and perform cleanup.
        
        This method should be called when the application is shutting down
        to ensure proper cleanup of MCP server connections.
        
        Returns:
            Dict[str, bool]: Dictionary mapping server IDs to disconnection success status
        """
        self.logger.info("Shutting down MCP servers...")
        return await self.disconnect_servers()