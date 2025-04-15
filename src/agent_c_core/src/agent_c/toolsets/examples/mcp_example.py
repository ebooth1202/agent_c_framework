"""Example usage of the MCP Tool Chest.

This example shows how to create an MCPToolChest, load server configurations,
and use MCP tools with an Agent C agent.
"""

import asyncio
import logging
import os
from pathlib import Path

from agent_c.agents import ClaudeChatAgent
from agent_c.toolsets.mcp_tool_chest import MCPToolChest


async def main():
    """Main example function."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create an MCP-enabled tool chest
    mcp_tool_chest = MCPToolChest()
    
    # Get the current directory to find the config file
    current_dir = Path(__file__).parent
    config_file = current_dir / "mcp_servers.yaml"
    
    # Load configuration from a file
    mcp_tool_chest.load_config(str(config_file))
    
    # Add a server programmatically (optional example)
    mcp_tool_chest.add_server(
        "calculator",
        command="python",
        args=["-m", "calculator_server"],
        env={"API_KEY": os.environ.get("API_KEY", "")}
    )
    
    # Initialize the tool chest (connects to servers)
    await mcp_tool_chest.init_tools()
    
    # Use like a regular tool chest in an agent
    # (assuming you have a Claude API key in the environment)
    agent = ClaudeChatAgent(tool_chest=mcp_tool_chest)
    
    # Example conversation using MCP tools
    messages = await agent.chat("Hello! Can you list the tools you have available?")
    print(messages)
    
    # Clean up when done
    await mcp_tool_chest.disconnect_servers()


if __name__ == "__main__":
    asyncio.run(main())