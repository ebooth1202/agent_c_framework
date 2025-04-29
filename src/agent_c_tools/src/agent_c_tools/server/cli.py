"""Command-line interface for the MCP ToolChest Server.

This module provides a command-line interface for running the MCPToolChestServer,
making it easy to start a server from the command line with various configuration options.
"""
import logging
import sys
import argparse


from agent_c.toolsets import MCPToolChest
from .mcp_server import MCPToolChestServer


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
    
    # Determine MCP servers configuration file
    mcp_servers_config_path = args.mcp_servers_config
    if mcp_servers_config_path:
        logger.info(f"Using MCP servers configuration from {mcp_servers_config_path}")
        
    # Handle SSE server configuration from command line
    if args.sse_url:
        logger.info(f"Adding SSE MCP server configuration for {args.sse_server_id}")
        # If no config path provided, create an empty one
        if not config_path:
            import tempfile
            import yaml
            
            # Create a temporary config file with the SSE server configuration
            temp_config = {
                "server": {
                    "mcp_servers": {
                        "servers": {
                            args.sse_server_id: {
                                "transport_type": "sse",
                                "url": args.sse_url
                            }
                        }
                    }
                }
            }
            
            # Add headers if provided
            if args.sse_headers:
                try:
                    import json
                    headers = json.loads(args.sse_headers)
                    temp_config["server"]["mcp_servers"]["servers"][args.sse_server_id]["headers"] = headers
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in --sse-headers, ignoring")
            
            # Add timeout if provided
            if args.sse_timeout is not None:
                temp_config["server"]["mcp_servers"]["servers"][args.sse_server_id]["timeout"] = args.sse_timeout
            
            # Write temporary config file
            temp_file = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)
            with open(temp_file.name, "w") as f:
                yaml.dump(temp_config, f)
            
            config_path = temp_file.name
            logger.info(f"Created temporary config file at {config_path}")
        else:
            # We have an existing config file, so we'll just set environment variables
            # to add the SSE server configuration
            import os
            import json
            
            os.environ["MCP_SERVER_SSE_URL"] = args.sse_url
            os.environ["MCP_SERVER_SSE_ID"] = args.sse_server_id
            
            if args.sse_headers:
                os.environ["MCP_SERVER_SSE_HEADERS"] = args.sse_headers
            
            if args.sse_timeout is not None:
                os.environ["MCP_SERVER_SSE_TIMEOUT"] = str(args.sse_timeout)
    


    tool_chest = MCPToolChest()

    
    # Create the server - tool initialization will happen inside the server
    server = MCPToolChestServer(
        tool_chest=tool_chest,
        config_path=config_path,
        server_config=server_config,
        mcp_servers_config_path=mcp_servers_config_path
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
    
    # Server configuration options
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to server configuration file"
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
    
    # Tool configuration options
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
    
    # MCP-specific options
    parser.add_argument(
        "--mcp-servers-config", 
        type=str, 
        help="Path to MCP servers configuration file (YAML or JSON)"
    )
    parser.add_argument(
        "--use-mcp-toolchest", 
        action="store_true", 
        help="Always use MCPToolChest even without MCP server configurations"
    )
    
    # SSE transport options
    parser.add_argument(
        "--sse-url", 
        type=str, 
        help="URL for SSE transport to an MCP server"
    )
    parser.add_argument(
        "--sse-server-id", 
        type=str, 
        default="default_sse_server",
        help="ID for the SSE MCP server (default: default_sse_server)"
    )
    parser.add_argument(
        "--sse-headers", 
        type=str, 
        help="JSON string of headers for SSE transport (e.g., '{\"Authorization\": \"Bearer token\"}')"
    )
    parser.add_argument(
        "--sse-timeout", 
        type=float, 
        help="Timeout in seconds for SSE transport"
    )
    
    # Other options
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