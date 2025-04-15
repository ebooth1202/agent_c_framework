"""Example demonstrating the use of the MCP Tool Chest in Agent C.

This example shows how to:
1. Configure the MCPToolChest with server configurations
2. Initialize MCP servers and discover tools
3. Use MCP tools from an Agent C agent

Requires an MCP server to be running for actual tool execution.
"""

import asyncio
import logging
import os
import json

from agent_c.toolsets import MCPToolChest
from agent_c.agents import Agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Example configuration for an MCP server
MCP_CONFIG = {
    "servers": {
        "example_server": {
            "command": "python -m mcp.examples.simple_server",
            "args": [],
            "env": {
                "MCP_EXAMPLE_ENV": "value"
            }
        }
    }
}

# Save the configuration to a file
def save_config():
    os.makedirs("./configs", exist_ok=True)
    with open("./configs/mcp_config.json", "w") as f:
        json.dump(MCP_CONFIG, f, indent=2)
    return "./configs/mcp_config.json"

async def run_example():
    # Create an MCP Tool Chest
    chest = MCPToolChest()
    
    # Method 1: Load configuration from a file
    config_path = save_config()
    chest.load_config(config_path)
    
    # Method 2: Add a server programmatically
    chest.add_server(
        "another_server",
        command="python -m mcp.examples.another_server",
        args=["--port", "8080"],
        env={"DEBUG": "true"}
    )
    
    # Initialize the tool chest (connects to MCP servers)
    await chest.init_tools()
    
    # Create an Agent C agent with the MCP Tool Chest
    agent = Agent(tool_chest=chest)
    
    # Use MCP tools via the agent
    prompt = """
    I need your help with some tasks. Please use the available MCP tools to:
    1. Get the current weather for San Francisco
    2. Calculate 1234 * 5678
    3. Generate a summary of the text: "Agent C is a powerful framework for building AI agents with tool use capabilities."
    """
    
    # Run the agent with the prompt
    response = await agent.chat(prompt)
    print("Agent Response:")
    print(response)
    
    # Clean up MCP server connections
    await chest.shutdown()

if __name__ == "__main__":
    asyncio.run(run_example())