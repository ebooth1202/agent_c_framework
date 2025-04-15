"""Command-line interface for the MCP ToolChest Server.

This module provides a command-line interface for running the MCPToolChestServer,
making it easy to start a server from the command line with various configuration options.
"""
import logging
import sys
import argparse

from agent_c.toolsets import ToolChest
from agent_c_tools.server.mcp_server import MCPToolChestServer


def configure_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def run_server(args: argparse.Namespace) -> None:
    """Run the MCP ToolChest Server with the specified arguments.
    
    Args:
        args: Command-line arguments
    """
    # Configure logging
    configure_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting MCP ToolChest Server")
    
    # Create server configuration
    server_config = {}
    
    # Load configuration from file if specified
    config_path = None
    if args.config:
        config_path = args.config
        logger.info(f"Loading configuration from {config_path}")
    
    # Override configuration with command-line arguments
    if args.name:
        server_config["name"] = args.name
    if args.host:
        server_config["host"] = args.host
    if args.port:
        server_config["port"] = args.port
    if args.allow_tool:
        server_config["allowed_tools"] = args.allow_tool
    
    # Prepare the tool chest synchronously - initialization will happen in the server
    tool_chest = ToolChest()
    
    # Create the server - tool initialization will happen inside the server
    server = MCPToolChestServer(
        tool_chest=tool_chest,
        config_path=config_path,
        server_config=server_config
    )
    
    # Run the server - this will block until the server is stopped
    # Let the MCP server manage its own event loop
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    finally:
        logger.info("Server stopped")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run the Agent C Tools MCP server.")
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        help="Port to listen on (default: 8027)"
    )
    parser.add_argument(
        "--name", 
        type=str, 
        help="Server name (default: agent_c_tools)"
    )
    parser.add_argument(
        "--allow-tool", 
        type=str, 
        action="append", 
        help="Allow a specific tool or pattern (can be used multiple times)"
    )
    parser.add_argument(
        "--discover-package", 
        type=str, 
        action="append", 
        help="Discover tools from package (can be used multiple times)"
    )
    parser.add_argument(
        "--import-package", 
        type=str, 
        action="append", 
        help="Import a package with tools (can be used multiple times)"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    try:
        # Run the server directly - no asyncio.run() needed
        run_server(args)
    except KeyboardInterrupt:
        print("\nServer shutdown requested. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()