"""Configuration handling for the MCP ToolChest Server.

This module provides classes and functions for loading and managing
server configuration from files, environment variables, and direct settings.
"""

import os
import re
import json
import yaml
import logging

from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Union


def _resolve_env_vars(value: str) -> str:
    """Resolve environment variables in a string.
    
    Supports ${VAR} and $VAR syntax.
    
    Args:
        value: String that may contain environment variable references
        
    Returns:
        String with environment variables resolved
    """
    # Pattern to match ${VAR} syntax
    pattern1 = re.compile(r'\${([^}]+)}')
    # Pattern to match $VAR syntax
    pattern2 = re.compile(r'\$([a-zA-Z0-9_]+)')
    
    # Replace ${VAR} with environment variable value
    def replace_env_var(match):
        env_var = match.group(1)
        return os.environ.get(env_var, f"${{{env_var}}}")
    
    # First replace ${VAR} syntax
    value = pattern1.sub(replace_env_var, value)
    # Then replace $VAR syntax
    value = pattern2.sub(lambda m: os.environ.get(m.group(1), f"${m.group(1)}"), value)
    
    return value


def _process_config_values(config: Dict[str, Any]) -> Dict[str, Any]:
    """Process configuration values, resolving environment variables.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Processed configuration with environment variables resolved
    """
    result = {}
    
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = _process_config_values(value)
        elif isinstance(value, list):
            result[key] = [_process_item(item) for item in value]
        elif isinstance(value, str):
            result[key] = _resolve_env_vars(value)
        else:
            result[key] = value
            
    return result


def _process_item(item: Any) -> Any:
    """Process a single configuration item.
    
    Args:
        item: Configuration item
        
    Returns:
        Processed configuration item
    """
    if isinstance(item, dict):
        return _process_config_values(item)
    elif isinstance(item, list):
        return [_process_item(sub_item) for sub_item in item]
    elif isinstance(item, str):
        return _resolve_env_vars(item)
    else:
        return item


@dataclass
class SecurityConfig:
    """Security configuration for the MCP ToolChest Server."""
    allowed_tools: List[str] = field(default_factory=lambda: ["*"])  # Default to allow all tools
    allowed_patterns: List[Pattern] = field(default_factory=list)  # Compiled patterns
    
    def __post_init__(self):
        """Compile allowed_tools patterns."""
        self.allowed_patterns = [re.compile(pat.replace("*", ".*")) for pat in self.allowed_tools]
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed based on pattern matching.
        
        Args:
            tool_name: The tool name to check (in format namespace-tool)
                
        Returns:
            True if the tool is allowed, False otherwise
        """
        return any(pattern.fullmatch(tool_name) for pattern in self.allowed_patterns)


@dataclass
class MCPServerConfig:
    """Configuration for an individual MCP server.
    
    This class supports both STDIO and SSE transport configurations. For STDIO transport,
    provide command, args, and env. For SSE transport, provide url and optionally headers
    and timeout.
    """
    # Common fields
    transport_type: str = "stdio"  # "stdio" or "sse"
    
    # STDIO transport fields
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    
    # SSE transport fields
    url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[float] = None


@dataclass
class MCPServersConfig:
    """Configuration for MCP servers to connect to."""
    servers: Dict[str, MCPServerConfig] = field(default_factory=dict)
    config_file: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> 'MCPServersConfig':
        """Load MCP servers configuration from a file.
        
        Args:
            config_path: Path to a configuration file (YAML or JSON)
            
        Returns:
            MCPServersConfig loaded from the file
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is invalid
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"MCP servers configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ('.yaml', '.yml'):
                config_dict = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
        
        # Process environment variables and other special values
        config_dict = _process_config_values(config_dict)
        
        # Create servers dictionary
        servers = {}
        for server_id, server_config in config_dict.get("servers", {}).items():
            # Determine transport type
            transport_type = server_config.get("transport_type", "stdio")
            
            # For SSE transport, url is required
            if transport_type == "sse" and "url" not in server_config:
                raise ValueError(f"MCP server {server_id} is configured for SSE transport but no URL is provided")
            
            # For STDIO transport, command is required
            if transport_type == "stdio" and not server_config.get("command"):
                raise ValueError(f"MCP server {server_id} is configured for STDIO transport but no command is provided")
                
            servers[server_id] = MCPServerConfig(
                transport_type=transport_type,
                command=server_config.get("command"),
                args=server_config.get("args", []),
                env=server_config.get("env", {}),
                url=server_config.get("url"),
                headers=server_config.get("headers", {}),
                timeout=server_config.get("timeout")
            )
        
        # Create and return MCPServersConfig
        return cls(
            servers=servers,
            config_file=str(path)
        )


@dataclass
class ToolsConfig:
    """Configuration for tool discovery and loading."""
    discover: List[str] = field(default_factory=lambda: ["agent_c_tools.tools"])
    imports: List[str] = field(default_factory=list)
    config: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ServerConfig:
    """Configuration for the MCP ToolChest Server."""
    name: str = "agent_c"
    host: str = "127.0.0.1"
    port: int = 8027
    security: SecurityConfig = field(default_factory=SecurityConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    mcp_servers: MCPServersConfig = field(default_factory=MCPServersConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ServerConfig':
        """Load configuration from a file.
        
        Args:
            config_path: Path to a configuration file (YAML or JSON)
            
        Returns:
            ServerConfig loaded from the file
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is invalid
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ('.yaml', '.yml'):
                config_dict = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
        
        # Process environment variables and other special values
        config_dict = _process_config_values(config_dict)
        
        # Extract server configuration
        server_config = config_dict.get('server', {})
        security_config = server_config.pop('security', {})
        tools_config = server_config.pop('tools', {})
        mcp_servers_config = server_config.pop('mcp_servers', {})
        
        # Create security config
        security = SecurityConfig(
            allowed_tools=security_config.get('allowed_tools', ["*"])
        )
        
        # Create tools config
        tools = ToolsConfig(
            discover=tools_config.get('discover', ["agent_c_tools.tools"]),
            imports=tools_config.get('imports', []),
            config=tools_config.get('config', {})
        )
        
        # Create MCP servers config
        mcp_servers = MCPServersConfig()
        if 'config_file' in mcp_servers_config:
            try:
                mcp_servers = MCPServersConfig.from_file(mcp_servers_config['config_file'])
            except (FileNotFoundError, ValueError) as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not load MCP servers config file: {e}")
        elif 'servers' in mcp_servers_config:
            servers = {}
            for server_id, server_config in mcp_servers_config.get('servers', {}).items():
                # Determine transport type
                transport_type = server_config.get('transport_type', 'stdio')
                
                # For SSE transport, url is required
                if transport_type == 'sse' and 'url' not in server_config:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"MCP server {server_id} is configured for SSE transport but no URL is provided")
                    continue
                
                # For STDIO transport, command is required
                if transport_type == 'stdio' and not server_config.get('command'):
                    logger = logging.getLogger(__name__)
                    logger.warning(f"MCP server {server_id} is configured for STDIO transport but no command is provided")
                    continue
                    
                servers[server_id] = MCPServerConfig(
                    transport_type=transport_type,
                    command=server_config.get('command'),
                    args=server_config.get('args', []),
                    env=server_config.get('env', {}),
                    url=server_config.get('url'),
                    headers=server_config.get('headers', {}),
                    timeout=server_config.get('timeout')
                )
            mcp_servers = MCPServersConfig(servers=servers)
        
        # Create and return server config
        # Extract only the parameters that the ServerConfig constructor expects
        # to avoid "unexpected keyword argument" errors
        name = server_config.pop('name', 'agent_c')
        host = server_config.pop('host', '127.0.0.1')
        port = server_config.pop('port', 8027)
        
        # If there are any keys left in server_config, log a warning as they will be ignored
        if server_config:
            logger = logging.getLogger(__name__)
            logger.warning(f"Ignoring unexpected server configuration keys: {', '.join(server_config.keys())}")
        
        return cls(
            name=name,
            host=host,
            port=port,
            security=security,
            tools=tools,
            mcp_servers=mcp_servers
        )
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Load configuration from environment variables.
        
        Environment variables:
            MCP_SERVER_NAME: Server name
            MCP_SERVER_HOST: Host to bind to
            MCP_SERVER_PORT: Port to listen on
            MCP_SERVER_ALLOWED_TOOLS: Comma-separated list of allowed tool patterns
            MCP_SERVER_DISCOVER: Comma-separated list of packages to discover tools from
            MCP_SERVER_IMPORTS: Comma-separated list of packages to import
            MCP_SERVERS_CONFIG_FILE: Path to MCP servers configuration file
            
        Returns:
            ServerConfig loaded from environment variables
        """
        name = os.environ.get('MCP_SERVER_NAME', "Agent C Tools Server")
        host = os.environ.get('MCP_SERVER_HOST', "127.0.0.1")
        port = int(os.environ.get('MCP_SERVER_PORT', "8000"))
        
        allowed_tools = os.environ.get('MCP_SERVER_ALLOWED_TOOLS', "*")
        allowed_tools = [t.strip() for t in allowed_tools.split(',')]
        
        discover = os.environ.get('MCP_SERVER_DISCOVER', "agent_c_tools.tools")
        discover = [d.strip() for d in discover.split(',')]
        
        imports = os.environ.get('MCP_SERVER_IMPORTS', "")
        imports = [i.strip() for i in imports.split(',')] if imports else []
        
        # Handle MCP servers config file
        mcp_servers = MCPServersConfig()
        mcp_servers_config_file = os.environ.get('MCP_SERVERS_CONFIG_FILE')
        if mcp_servers_config_file:
            try:
                mcp_servers = MCPServersConfig.from_file(mcp_servers_config_file)
            except (FileNotFoundError, ValueError) as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not load MCP servers config file: {e}")
        
        # Handle direct SSE server configuration via environment variables
        mcp_server_sse_url = os.environ.get('MCP_SERVER_SSE_URL')
        if mcp_server_sse_url:
            server_id = os.environ.get('MCP_SERVER_SSE_ID', 'default_sse_server')
            headers_str = os.environ.get('MCP_SERVER_SSE_HEADERS', '{}')
            try:
                headers = json.loads(headers_str)
            except json.JSONDecodeError:
                logger = logging.getLogger(__name__)
                logger.warning(f"Invalid JSON in MCP_SERVER_SSE_HEADERS, using empty headers")
                headers = {}
            
            timeout_str = os.environ.get('MCP_SERVER_SSE_TIMEOUT')
            timeout = float(timeout_str) if timeout_str else None
            
            # Add the SSE server configuration
            mcp_servers.servers[server_id] = MCPServerConfig(
                transport_type='sse',
                url=mcp_server_sse_url,
                headers=headers,
                timeout=timeout
            )
        
        return cls(
            name=name,
            host=host,
            port=port,
            security=SecurityConfig(allowed_tools=allowed_tools),
            tools=ToolsConfig(discover=discover, imports=imports),
            mcp_servers=mcp_servers
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        result = {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "allowed_tools": self.security.allowed_tools,
            "dependencies": []  # No dependencies by default
        }
        
        # Add MCP servers configuration if any servers are defined
        if self.mcp_servers.servers:
            result["mcp_servers"] = {
                server_id: {
                    "command": server.command,
                    "args": server.args,
                    "env": server.env
                } for server_id, server in self.mcp_servers.servers.items()
            }
            
        return result