# Agent C MCP Protocol Support

## Overview

The Message Control Protocol (MCP) provides a standardized way for AI agents to interact with external tools and services. Agent C includes comprehensive support for both consuming MCP tools from external servers and exposing Agent C toolsets as MCP servers.

This documentation covers the key components for MCP integration and provides examples for common use cases.

## Core Components

### MCPServer

The `MCPServer` class in `agent_c.toolsets.mcp_server` represents a connection to an external MCP server. It handles:

- Connection establishment and lifecycle management
- Tool discovery from external MCP servers
- Tool execution through the MCP protocol
- Error handling and reconnection logic

### MCPToolset

The `MCPToolset` class in `agent_c.toolsets.mcp_toolset` acts as a bridge between external MCP tools and Agent C's toolset system. It:

- Dynamically creates Agent C tools from MCP server tool definitions
- Handles parameter translation and validation
- Provides proper documentation and schemas for MCP tools

### MCPToolChest

The `MCPToolChest` class in `agent_c.toolsets.mcp_tool_chest` extends the standard `ToolChest` with MCP-specific functionality. It:

- Manages multiple MCP server connections
- Loads configurations from files (YAML or JSON)
- Handles initialization and shutdown of all MCP connections
- Provides centralized access to tools from multiple MCP servers

## Using External MCP Tools

### Basic Setup

To use tools from an external MCP server:

```python
from agent_c import MCPToolChest

# Create an MCP-enabled tool chest
tool_chest = MCPToolChest()

# Add a server configuration
tool_chest.add_server(
    server_id="calculator",
    command="python",
    args=["-m", "calculator_mcp_server"],
    env={"PYTHONPATH": "."}  # Optional environment variables
)

# Initialize tools (connects to servers)
await tool_chest.init_tools()

# Use tools through the standard call_tools mechanism
results = await tool_chest.call_tools([
    {
        "id": "calc-1",
        "name": "mcp_calculator-add",
        "parameters": {"a": 5, "b": 3}
    }
])
```

### Loading Configuration from File

You can define MCP servers in a configuration file (YAML or JSON):

```yaml
# mcp_config.yaml
servers:
  calculator:
    command: python
    args: ["-m", "calculator_mcp_server"]
    env:
      PYTHONPATH: "."
  data_processor:
    command: node
    args: ["data_processor_server.js"]
```

Then load it in your code:

```python
from agent_c import MCPToolChest

# Create and load config
tool_chest = MCPToolChest()
tool_chest.load_config("mcp_config.yaml")

# Initialize tools
await tool_chest.init_tools()
```

## Exposing Agent C Tools as an MCP Server

The `agent_c_tools` package provides `MCPToolChestServer` to expose Agent C tools via the MCP protocol.

### Basic Server

```python
from agent_c import ToolChest
from agent_c_tools.server import MCPToolChestServer

# Create a tool chest with your tools
tool_chest = ToolChest()
# ... add your tools ...
await tool_chest.init_tools()

# Create and run the server
server = MCPToolChestServer(tool_chest=tool_chest)

# The run method blocks until the server stops
server.run()
```

### Server with Configuration

```python
from agent_c_tools.server import MCPToolChestServer

# Create a server from config file
server = MCPToolChestServer(config_path="server_config.yaml")

# Start the server
server.run()
```

### Secure Server

```python
from agent_c_tools.server import MCPToolChestServer

# Configure a secure server
server = MCPToolChestServer(
    server_config={
        "name": "Secure Tool Server",
        "host": "0.0.0.0",  # Listen on all interfaces
        "port": 8443,       # Custom port
        "allowed_tools": ["filesystem-*", "database-query"]  # Tool pattern whitelist
    }
)

# Start the server
server.run()
```

## Server Configuration File

A server configuration file can include the following sections:

```yaml
# MCP server configuration
name: "Agent C Tool Server"
host: "127.0.0.1"
port: 8000

# Tool configuration
tools:
  discover: true  # Auto-discover tools
  imports:  # Additional modules to import
    - "my_tools.custom_tools"
  config:  # Tool-specific configuration
    filesystem:
      root_dir: "/data"
      allow_writes: true

# Security settings
security:
  allowed_tools:  # Tool pattern whitelist
    - "filesystem-read_*"
    - "calculator-*"
  disallowed_tools:  # Tool pattern blacklist
    - "filesystem-delete_*"
```

## Tool Patterns

Tool patterns use glob-style matching to specify which tools are allowed or disallowed:

- `*` matches any number of characters within a segment
- `toolset-*` matches all tools in a specific toolset
- `*-read_*` matches all tools with "read_" in their name from any toolset

## Lifecycle Management

Both client connections and servers need proper lifecycle management:

### Client Lifecycle

```python
from agent_c import MCPToolChest

# Create and initialize
tool_chest = MCPToolChest()
# ... add servers ...
await tool_chest.init_tools()

# Use tools...

# Shutdown when done
await tool_chest.shutdown()
```

### Server Lifecycle

```python
from agent_c_tools.server import MCPToolChestServer

# Create server
server = MCPToolChestServer()

# Start server (blocks until stopped)
server.run()

# Note: For programmatic control, the server.stop() method can be called
# from another thread to stop the server
```

## Advanced Usage

### Custom Tool Authentication

Tool authentication can be implemented by extending `MCPToolChestServer` and overriding the tool implementation methods to add authentication checks.

### Rate Limiting

Rate limiting can be implemented by extending `MCPToolChestServer` and adding rate limiting logic to the tool implementation.

### Multiple Server Support

You can run multiple MCP servers on different ports to separate tool sets or implement different security boundaries:

```python
from agent_c import ToolChest
from agent_c_tools.server import MCPToolChestServer
import threading

# Create tool chests
public_tools = ToolChest()
private_tools = ToolChest()

# Initialize tools
await public_tools.init_tools()
await private_tools.init_tools()

# Create servers
public_server = MCPToolChestServer(
    tool_chest=public_tools,
    server_config={"port": 8000}
)

private_server = MCPToolChestServer(
    tool_chest=private_tools,
    server_config={"port": 8001}
)

# Start servers in separate threads
threading.Thread(target=public_server.run).start()
threading.Thread(target=private_server.run).start()
```

## Troubleshooting

### Common Issues

- **Server Connection Failures**: Ensure the MCP server is running and accessible from the client system. Check firewall settings and network connectivity.

- **Tool Not Found**: Verify that the tool name matches exactly the name provided by the server. Tool names are case-sensitive.

- **Parameter Errors**: Make sure all required parameters are provided and have the correct types. The MCP protocol does strict type checking.

### Enabling Debug Logging

To enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agent_c.mcp")
logger.setLevel(logging.DEBUG)
```