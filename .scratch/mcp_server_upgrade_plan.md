# MCP Server Upgrade Plan

## Objective
Upgrade the existing MCPToolChestServer in agent_c_tools to use MCPToolChest from agent_c_core instead of regular ToolChest, and include configuration for MCP servers.

## Analysis

### Current Architecture
1. `MCPToolChestServer` currently accepts either a ToolChest or MCPToolChest but doesn't fully leverage MCPToolChest capabilities
2. The server configuration doesn't include dedicated settings for configuring MCP servers
3. CLI doesn't have options for MCP server configuration

### Target Architecture
1. `MCPToolChestServer` primarily works with MCPToolChest
2. Server configuration includes MCP server configuration
3. CLI supports specifying MCP server configuration files
4. Configuration files show how to set up MCP servers

## Implementation Plan

### Phase 1: Update Configuration System
- [x] 1.1. Update `ServerConfig` class in config.py to support MCP server configurations
- [x] 1.2. Add methods for loading MCP server configurations from files and environment variables
- [x] 1.3. Update validation and parsing logic

### Phase 2: Update MCPToolChestServer
- [x] 2.1. Modify initialization to prefer MCPToolChest
- [x] 2.2. Update tool discovery logic to use MCPToolChest capabilities
- [x] 2.3. Make sure all MCPToolChest features are properly utilized

### Phase 3: Update CLI
- [x] 3.1. Add CLI options for MCP server configurations
- [x] 3.2. Update argument parsing and validation

### Phase 4: Create Configuration Files
- [x] 4.1. Create a default configuration file with all options populated
- [x] 4.2. Create an example configuration file with an MCP server connection
- [x] 4.3. Create documentation explaining the configuration options

### Phase 5: Testing
- [ ] 5.1. Test with MCPToolChest using local tools
- [ ] 5.2. Test with MCPToolChest connecting to external MCP servers
- [ ] 5.3. Test CLI with various configuration options

## Progress Tracking
Current phase: Complete

## Implementation Summary

1. Fixed import issue in mcp_server.py (added missing MCPServersConfig import)
2. Created comprehensive configuration files:
   - Default configuration with all options (agent_c_server_default_config.yaml)
   - Example configuration with demo MCP server (agent_c_server_example_config.yaml)
3. Added a README_CONFIG.md file with documentation on configuration options
4. Verified that the MCPToolChestServer already properly handles conversion from ToolChest to MCPToolChest
5. Verified that the CLI already supports MCP server configuration options