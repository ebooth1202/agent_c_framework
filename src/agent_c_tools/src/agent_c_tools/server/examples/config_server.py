"""Example of using an MCPToolChestServer with a configuration file.

This example demonstrates how to create an MCP server using a configuration
file to specify tools, security settings, and other options.
"""

import logging
import os
from pathlib import Path

from agent_c.toolsets import ToolChest
from agent_c_tools.server import MCPToolChestServer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a sample configuration file if it doesn't exist
def create_sample_config():
    config_path = Path("mcp_server_config.yaml")
    
    if not config_path.exists():
        sample_config = """
# MCP ToolChest Server configuration
server:
  name: "Agent C Tools Server"
  host: "127.0.0.1"
  port: 8000
  security:
    allowed_tools: ["*"]  # Allow all tools
    # allowed_tools: ["web-*", "weather-*"]  # Allow specific namespaces

tools:
  # Auto-discover tools from these packages
  discover:
    - "agent_c_tools.tools"
  
  # Additional tool packages to import
  imports: []
  
  # Configuration for specific tools
  config:
    weather:
      api_key: "${WEATHER_API_KEY}"  # Use environment variable
    web_search:
      google_api_key: "your-key-here"
"""
        with open(config_path, "w") as f:
            f.write(sample_config)
        
        logger.info(f"Created sample configuration file: {config_path}")
    
    return config_path

def main():
    # Create sample config if needed
    config_path = create_sample_config()
    
    # Create a ToolChest for tools
    tool_chest = ToolChest()
    
    # Create the server with the configuration file
    server = MCPToolChestServer(tool_chest, config_path=str(config_path))
    
    # Log info about the server before running
    logger.info(f"MCP server will start at http://{server.config.host}:{server.config.port}")
    logger.info("The server will be available for MCP clients to connect")
    logger.info("Press Ctrl+C to stop the server")
    
    # You can test the server using the MCP CLI tool:
    logger.info("\nTest with MCP CLI:")
    logger.info(f"mcp dev --url http://{server.config.host}:{server.config.port}")
    
    try:
        # Run the server - this will block until interrupted with Ctrl+C
        server.run()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    main()