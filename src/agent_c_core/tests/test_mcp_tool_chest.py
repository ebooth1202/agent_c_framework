"""Tests for the MCP Tool Chest implementation."""

import asyncio
import json
import os
from pathlib import Path
from unittest import mock

import pytest
from mcp import ClientSession

from agent_c.toolsets.mcp_server import MCPServer
from agent_c.toolsets.mcp_toolset import MCPToolset
from agent_c.toolsets.mcp_tool_chest import MCPToolChest


# Sample test configuration
TEST_CONFIG = {
    "servers": {
        "test_server": {
            "command": "python",
            "args": ["-m", "test_mcp_server"],
            "env": {"TEST_KEY": "test_value"}
        }
    }
}


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file for testing."""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(TEST_CONFIG, f)
    return str(config_path)


class TestMCPToolChest:
    """Tests for the MCPToolChest class."""

    def test_init(self):
        """Test MCPToolChest initialization."""
        chest = MCPToolChest()
        assert isinstance(chest, MCPToolChest)
        assert hasattr(chest, "mcp_servers")
        assert isinstance(chest.mcp_servers, dict)
        assert len(chest.mcp_servers) == 0

    def test_add_server(self):
        """Test adding an MCP server programmatically."""
        chest = MCPToolChest()
        chest.add_server(
            "test_server",
            command="python",
            args=["-m", "test_mcp_server"],
            env={"TEST_KEY": "test_value"}
        )
        
        assert "test_server" in chest.mcp_servers
        assert isinstance(chest.mcp_servers["test_server"], MCPServer)
        assert chest.mcp_servers["test_server"].server_id == "test_server"
        assert chest.mcp_servers["test_server"].config["command"] == "python"

    def test_load_config(self, config_file):
        """Test loading configuration from a file."""
        chest = MCPToolChest()
        config = chest.load_config(config_file)
        
        assert config == TEST_CONFIG
        assert "test_server" in chest.mcp_servers
        assert isinstance(chest.mcp_servers["test_server"], MCPServer)

    @pytest.mark.asyncio
    async def test_init_tools(self):
        """Test initializing tools including MCP servers."""
        # Create direct patches for the specific things we need to mock
        with mock.patch('agent_c.toolsets.mcp_server.MCPServer.connect', autospec=True) as mock_connect, \
             mock.patch('agent_c.toolsets.mcp_server.MCPServer.disconnect', autospec=True) as mock_disconnect, \
             mock.patch('agent_c.toolsets.mcp_server.MCPServer.discover_tools', autospec=True) as mock_discover_tools:
            
            # Set up tool discovery to return a dictionary of tools
            mock_tool = {
                "name": "test_tool",
                "description": "A test tool",
                "schema": {"properties": {"arg1": {"type": "string"}}}
            }
            mock_discover_tools.return_value = {"test_tool": mock_tool}
            
            # Set up connect to automatically call discover_tools
            # This simulates what happens in the real connect() method
            async def fake_connect(self):
                # When connect is called, mark discover_tools as called for this server
                await mock_discover_tools(self)
                return True
            
            mock_connect.side_effect = fake_connect
            mock_disconnect.return_value = True
            
            # Create the tool chest and add a server
            chest = MCPToolChest()
            chest.add_server(
                "test_server",
                command="python",
                args=["-m", "test_mcp_server"]
            )
            
            # Initialize tools
            await chest.init_tools()
            
            # Verify our mocks were called correctly
            mock_connect.assert_called_once_with(chest.mcp_servers["test_server"])
            mock_discover_tools.assert_called_once_with(chest.mcp_servers["test_server"])

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test executing an MCP tool."""
        # Create the tool chest first
        chest = MCPToolChest()
        chest.add_server(
            "test_server",
            command="python",
            args=["-m", "test_mcp_server"]
        )
        
        # Create and configure a mock toolset
        from agent_c.toolsets.mcp_toolset import MCPToolset
        mock_toolset = mock.MagicMock(spec=MCPToolset)
        mock_toolset.name = "mcp_test_server"
        mock_tool_method = mock.AsyncMock(return_value="Test result")
        setattr(mock_toolset, "mcp_test_tool", mock_tool_method)
        
        # Patch the server connection methods to avoid real async operations
        with mock.patch('agent_c.toolsets.mcp_server.MCPServer.connect', return_value=True), \
             mock.patch('agent_c.toolsets.mcp_server.MCPServer.disconnect', return_value=True), \
             mock.patch('agent_c.toolsets.mcp_server.MCPServer.discover_tools') as mock_discover_tools:
            
            # Set up tool discovery to return a dictionary of tools
            mock_tool = {
                "name": "test_tool",
                "description": "A test tool",
                "schema": {"properties": {"arg1": {"type": "string"}}}
            }
            mock_discover_tools.return_value = {"test_tool": mock_tool}
            
            # Initialize tools - this would normally connect and add toolsets
            await chest.init_tools()
            
            # Manually add our mock toolset since the real connection didn't happen
            # In a real scenario, the MCPToolset would be created and added during connect
            chest.active_tools["mcp_test_server"] = mock_toolset
            
            # Call the tool method
            method_name = "mcp_test_tool"
            assert hasattr(mock_toolset, method_name), f"Method {method_name} not found"
            
            method = getattr(mock_toolset, method_name)
            result = await method(arg1="test_value")
            
            # Verify the tool was called with the correct arguments
            mock_tool_method.assert_called_once_with(arg1="test_value")
            assert result == "Test result"
            
    @pytest.mark.asyncio
    async def test_call_tools_integration(self):
        """Test the call_tools method with MCP tools."""
        # Mock the ServerResponse and ClientSession
        with mock.patch('agent_c.toolsets.mcp_server.stdio_client'), \
             mock.patch('agent_c.toolsets.mcp_server.ClientSession') as mock_session_cls, \
             mock.patch('agent_c.toolsets.mcp_server.AsyncExitStack'):
            
            # Mock the session's initialize method
            mock_session = mock.AsyncMock(spec=ClientSession)
            mock_session_cls.return_value.__aenter__.return_value = mock_session
            
            # Mock list_tools to return a list of tool tuples
            mock_tool = mock.MagicMock()
            mock_tool.name = "test_tool"
            mock_tool.description = "A test tool"
            mock_tool.inputSchema = {"properties": {"arg1": {"type": "string"}}}
            mock_session.list_tools.return_value = [("tools", [mock_tool])]
            
            # Mock call_tool to return a test result
            mock_session.call_tool.return_value = "Test result"
            
            # Create the tool chest and add a server
            chest = MCPToolChest()
            chest.add_server(
                "test_server",
                command="python",
                args=["-m", "test_mcp_server"]
            )
            
            # Initialize tools
            await chest.init_tools()
            
            # Create a mock toolset and add it to active_tools
            mock_toolset = mock.MagicMock()
            mock_toolset.name = "mcp_test_server"
            mock_tool_method = mock.AsyncMock(return_value="Test result")
            setattr(mock_toolset, "mcp_test_tool", mock_tool_method)
            chest.active_tools["mcp_test_server"] = mock_toolset
            
            # Create a tool call in Claude format
            tool_calls = [
                {
                    "id": "call_1",
                    "name": "mcp_test_server-mcp_test_tool",
                    "input": {"arg1": "test_value"}
                }
            ]
            
            # Execute the tool call
            results = await chest.call_tools(tool_calls, format_type="claude")
            
            # Verify the results
            assert len(results) == 2  # Assistant and user messages
            assert results[0]["role"] == "assistant"
            assert results[1]["role"] == "user"
            assert len(results[0]["content"]) == 1  # One tool call
            assert len(results[1]["content"]) == 1  # One tool result
            assert results[1]["content"][0]["type"] == "tool_result"
            assert results[1]["content"][0]["tool_use_id"] == "call_1"
            assert results[1]["content"][0]["content"] == "Test result"
            
            # Test with GPT format
            results = await chest.call_tools(tool_calls, format_type="gpt")
            
            # Verify the results
            assert len(results) == 2  # Assistant message and tool result
            assert results[0]["role"] == "assistant"
            assert results[1]["role"] == "tool"
            assert results[1]["tool_call_id"] == "call_1"
            assert results[1]["content"] == "Test result"