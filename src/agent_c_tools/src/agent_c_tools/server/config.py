"""Configuration handling for the MCP ToolChest Server.

This module provides classes and functions for loading and managing
server configuration from files, environment variables, and direct settings.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Union
import yaml
import json
from pathlib import Path


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
        tools_config = config_dict.get('tools', {})
        
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
        
        # Create and return server config
        return cls(
            **server_config,
            security=security,
            tools=tools
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
        
        return cls(
            name=name,
            host=host,
            port=port,
            security=SecurityConfig(allowed_tools=allowed_tools),
            tools=ToolsConfig(discover=discover, imports=imports)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "allowed_tools": self.security.allowed_tools,
            "dependencies": []  # No dependencies by default
        }