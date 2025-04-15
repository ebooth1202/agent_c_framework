"""Example of creating an MCP tool aggregator server.

This example demonstrates how to create an MCP server that aggregates tools
from multiple external MCP servers and exposes them through a single endpoint.
"""

import asyncio
import logging
from agent_c.toolsets.mcp import MCPToolChest, MCPToolChestServer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Create an MCPToolChest that connects to multiple external MCP servers
    mcp_chest = MCPToolChest()
    
    # Add servers - in a real environment, these would be actual MCP servers
    # For the example, we'll use placeholder URLs that would be replaced with real ones
    mcp_chest.add_server(
        name="text-tools",
        url="http://text-processor:8080"
    )
    
    mcp_chest.add_server(
        name="math-tools",
        url="http://math-server:8081",
        # Adding authentication for this server
        auth={"type": "bearer", "token": "math-api-key"}
    )
    
    # For demo purposes, we'll disable actual connections since these are placeholders
    # In a real environment, you would remove this line
    mcp_chest.connect_enabled = False
    
    logger.info("Initialized MCPToolChest with connections to multiple MCP servers")
    logger.info("Note: For this example, actual connections are disabled")
    
    # In a real environment, you would initialize the tools
    # await mcp_chest.init_tools()
    
    # Configure the aggregator server
    server_config = {
        "host": "127.0.0.1",
        "port": 9000,
        # Add authentication to the aggregator
        "auth": {
            "api_keys": ["aggregator-key"],
            "header_name": "X-Aggregator-Key"
        },
        # Rate limiting for the aggregator
        "rate_limit": {
            "requests_per_minute": 60
        }
    }
    
    # Create the aggregator server
    server = MCPToolChestServer(mcp_chest, server_config=server_config)
    
    # In a real environment, you would start the server
    # However, since we're not actually connecting to the source servers in this example,
    # we'll just simulate it
    
    logger.info(f"In a real environment, the aggregator would start at http://{server_config['host']}:{server_config['port']}")
    logger.info("The aggregator would:")
    logger.info("1. Connect to all configured MCP servers")
    logger.info("2. Discover and import all available tools")
    logger.info("3. Expose those tools through a single, authenticated MCP endpoint")
    logger.info("4. Apply rate limiting and access control policies")
    logger.info("\nTo use this in production:")
    logger.info("1. Replace placeholder URLs with real MCP server endpoints")
    logger.info("2. Remove the 'connect_enabled = False' line")
    logger.info("3. Uncomment the calls to init_tools() and server.start()")
    
    # In a real environment, you'd run something like this:
    # await server.start()
    # try:
    #     while True:
    #         await asyncio.sleep(1)
    # except KeyboardInterrupt:
    #     await server.stop()
    
    logger.info("\nExample completed")

if __name__ == "__main__":
    asyncio.run(main())