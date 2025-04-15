"""Example of using an MCPToolChestServer to expose Agent C tools via MCP.

This example demonstrates how to create a simple MCP server that exposes
tools from the agent_c_tools package to external clients via the MCP protocol.
"""

import logging
from agent_c.toolsets import ToolChest
from agent_c_tools.server import MCPToolChestServer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Create a ToolChest for tools
    tool_chest = ToolChest()
    
    # Configure the server
    server_config = {
        "name": "Agent C Tools",
        "host": "127.0.0.1",
        "port": 8000
    }
    
    # Create the server - it will automatically discover tools
    # from the agent_c_tools.tools package
    server = MCPToolChestServer(tool_chest, server_config=server_config)
    
    # Log info about the server before running
    logger.info(f"MCP server will start at http://{server_config['host']}:{server_config['port']}")
    logger.info("The server will be available for MCP clients to connect")
    logger.info("Press Ctrl+C to stop the server")
    
    # You can test the server using the MCP CLI tool:
    logger.info("\nTest with MCP CLI:")
    logger.info("mcp dev --url http://127.0.0.1:8000")
    
    try:
        # Run the server - this will block until interrupted with Ctrl+C
        server.run()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    main()