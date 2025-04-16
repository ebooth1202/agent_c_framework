# Agent C Tools MCP Server

The Agent C Tools MCP Server provides a robust and configurable implementation of the Model Context Protocol (MCP) server for exposing Agent C tools to MCP clients.

## Features

- Automatic tool discovery from the agent_c_tools package
- Configuration via files, environment variables, or direct settings
- Tool filtering and access control
- Support for adding custom tools via imports
- Command-line interface for easy deployment
- Support for connecting to and integrating tools from external MCP servers
- MCPToolChest integration for enhanced MCP capabilities

## Installation

```bash
pip install agent_c-tools[mcp]  # Install with MCP dependencies
```

## Quick Start

### Command Line

Start the server with default settings:

```bash
mcp-tools-server
```

This will:

1. Discover all tools in the agent_c_tools.tools package
2. Start an MCP server on 127.0.0.1:8000
3. Expose all tools without filtering

### Custom Configuration

Start the server with a custom configuration file:

```bash
mcp-tools-server --config my_config.yaml
```

Example configuration file:

```yaml
# MCP ToolChest Server configuration
server:
  name: "Agent C Tools Server"
  host: "127.0.0.1"
  port: 8027
  security:
    allowed_tools: ["web-*", "weather-*", "think-*"]  # Only allow specific tools

tools:
  # Auto-discover tools from these packages
  discover:
    - "agent_c_tools.tools"
    - "my_custom_tools"

  # Additional tool packages to import
  imports:
    - "my_company.tools.special_tools"

  # Configuration for specific tools
  config:
    weather:
      api_key: "${WEATHER_API_KEY}"  # Use environment variable
    web_search:
      google_api_key: "your-key-here"
      
# MCP servers to connect to (optional)
mcp_servers:
  # Option 1: Reference an external config file
  config_file: "mcp_servers_config.yaml"
  
  # Option 2: Define servers directly in this file
  servers:
    calculator:
      command: python
      args: ["-m", "calculator_server"]
      env:
        API_KEY: "${CALCULATOR_API_KEY}"
```

Example MCP servers configuration file (mcp_servers_config.yaml):

```yaml
# MCP servers configuration
servers:
  # STDIO transport (process-based) MCP servers
  calculator:
    transport_type: "stdio"  # Optional, stdio is the default
    command: python
    args: ["-m", "calculator_server"]
    env:
      API_KEY: "${CALCULATOR_API_KEY}"
      
  filemanager:
    command: python
    args: ["filemanager.py"]
    env:
      ROOT_DIR: "/path/to/files"
      
  # SSE transport (HTTP-based) MCP servers
  claude_api:
    transport_type: "sse"
    url: "https://api.anthropic.com/v1/mcp/sse"
    headers:
      Authorization: "Bearer ${ANTHROPIC_API_KEY}"
      Content-Type: "application/json"
    timeout: 60.0
      
  custom_tools:
    transport_type: "sse"
    url: "http://localhost:8080/mcp/sse"
    headers:
      Authorization: "Bearer ${CUSTOM_API_KEY}"
    timeout: 30.0
```

## Command Line Options

```
Usage: mcp-tools-server [OPTIONS]

Run the Agent C Tools MCP server.

Options:
  --config PATH                 Path to server configuration file
  --host TEXT                   Host to bind to (default: 127.0.0.1)
  --port INTEGER                Port to listen on (default: 8027)
  --name TEXT                   Server name (default: Agent C Tools Server)
  --allow-tool TEXT             Allow a specific tool or pattern (can be used multiple times)
  --discover-package TEXT       Discover tools from package (can be used multiple times)
  --import-package TEXT         Import a package with tools (can be used multiple times)
  --mcp-servers-config PATH     Path to MCP servers configuration file (YAML or JSON)
  --use-mcp-toolchest           Always use MCPToolChest even without MCP server configurations
  
  # SSE transport options
  --sse-url TEXT                URL for SSE transport to an MCP server
  --sse-server-id TEXT          ID for the SSE MCP server (default: default_sse_server)
  --sse-headers TEXT            JSON string of headers for SSE transport
                                (e.g., '{"Authorization": "Bearer token"}')
  --sse-timeout FLOAT           Timeout in seconds for SSE transport
  
  --verbose, -v                 Enable verbose logging
  --help                        Show this message and exit
```

## Programmatic Usage

### Basic Usage

```python
import asyncio
from agent_c.toolsets import ToolChest
from agent_c_tools.server import MCPToolChestServer

async def main():
    # Create a ToolChest
    tool_chest = ToolChest()

    # Create and start the server
    server = MCPToolChestServer(tool_chest)
    await server.start()

    print(f"Server running at {server.config.host}:{server.config.port}")

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### With Custom Configuration

```python
import asyncio
from agent_c.toolsets import ToolChest
from agent_c_tools.server import MCPToolChestServer

async def main():
    # Create a ToolChest
    tool_chest = ToolChest()

    # Configure the server
    server_config = {
        "name": "Custom Tools Server",
        "host": "0.0.0.0",  # Allow external connections
        "port": 9000,
        "allowed_tools": ["web-*", "weather-*"]  # Only allow specific tools
    }

    # Create and start the server
    server = MCPToolChestServer(tool_chest, server_config=server_config)
    await server.start()

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using MCPToolChest with External MCP Servers

```python
from agent_c.toolsets import MCPToolChest
from agent_c_tools.server import MCPToolChestServer

def main():
    # Create an MCPToolChest that will connect to external MCP servers
    mcp_tool_chest = MCPToolChest()
    
    # Manually add MCP servers
    mcp_tool_chest.add_server(
        "calculator",
        command="python",
        args=["-m", "calculator_server"],
        env={"API_KEY": "your-key-here"}
    )
    
    # Or load from a config file
    # mcp_tool_chest.load_config("mcp_servers_config.yaml")
    
    # Create the server with the MCPToolChest
    server = MCPToolChestServer(
        tool_chest=mcp_tool_chest,  # Use MCPToolChest instead of normal ToolChest
        config_path="server_config.yaml"
    )
    
    # Run the server
    server.run()

if __name__ == "__main__":
    main()
```

## Testing with MCP CLI

Once the server is running, you can test it with the MCP CLI tool:

```bash
# Install the MCP CLI if needed
pip install "mcp[cli]"

# Connect to the server
mcp dev --url http://127.0.0.1:8027
```

## Integration with Claude Desktop

You can also install the server in Claude Desktop:

```bash
# Create a simple server script
echo 'from agent_c_tools.server.examples.basic_server import main; import asyncio; asyncio.run(main())' > tools_server.py

# Install in Claude Desktop
mcp install tools_server.py --name "Agent C Tools"
```

## Environment Variables

The server supports configuration via environment variables:

- `MCP_SERVER_NAME`: Server name
- `MCP_SERVER_HOST`: Host to bind to
- `MCP_SERVER_PORT`: Port to listen on
- `MCP_SERVER_ALLOWED_TOOLS`: Comma-separated list of allowed tool patterns
- `MCP_SERVER_DISCOVER`: Comma-separated list of packages to discover tools from
- `MCP_SERVER_IMPORTS`: Comma-separated list of packages to import
- `MCP_SERVERS_CONFIG_FILE`: Path to MCP servers configuration file

### SSE Transport Environment Variables

- `MCP_SERVER_SSE_URL`: URL for SSE transport to an MCP server
- `MCP_SERVER_SSE_ID`: ID for the SSE MCP server (default: default_sse_server)
- `MCP_SERVER_SSE_HEADERS`: JSON string of headers for SSE transport
- `MCP_SERVER_SSE_TIMEOUT`: Timeout in seconds for SSE transport

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.