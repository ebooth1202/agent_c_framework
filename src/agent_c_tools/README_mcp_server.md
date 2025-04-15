# Agent C Tools MCP Server

The Agent C Tools MCP Server provides a robust and configurable implementation of the Model Context Protocol (MCP) server for exposing Agent C tools to MCP clients.

## Features

- Automatic tool discovery from the agent_c_tools package
- Configuration via files, environment variables, or direct settings
- Tool filtering and access control
- Support for adding custom tools via imports
- Command-line interface for easy deployment

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
```

## Command Line Options

```
Usage: mcp-tools-server [OPTIONS]

Run the Agent C Tools MCP server.

Options:
  --config PATH                 Path to configuration file
  --host TEXT                   Host to bind to (default: 127.0.0.1)
  --port INTEGER                Port to listen on (default: 8000)
  --name TEXT                   Server name (default: Agent C Tools Server)
  --allow-tool TEXT             Allow a specific tool or pattern (can be used multiple times)
  --discover-package TEXT       Discover tools from package (can be used multiple times)
  --import-package TEXT         Import a package with tools (can be used multiple times)
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.