"""Tests for the MCP Server implementation."""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import AsyncExitStack
from typing import Dict, Any, Tuple

from agent_c.toolsets.mcp_server import MCPServer, TransportType, StdioTransport, SSETransport


class TestMCPServer:
    """Tests for the MCPServer class."""
    
    @pytest.fixture
    def stdio_config(self) -> Dict[str, Any]:
        """Return a sample STDIO configuration."""
        return {
            "transport_type": "stdio",
            "command": "python",
            "args": ["-m", "mcp.examples.server"],
            "env": {"DEBUG": "1"}
        }
    
    @pytest.fixture
    def sse_config(self) -> Dict[str, Any]:
        """Return a sample SSE configuration."""
        return {
            "transport_type": "sse",
            "url": "http://localhost:8000/mcp/sse",
            "headers": {"Authorization": "Bearer token123"},
            "timeout": 10.0,
            "sse_read_timeout": 600.0
        }
    
    def test_init_stdio(self, stdio_config):
        """Test initialization with STDIO transport."""
        server = MCPServer("test-stdio", stdio_config)
        assert server.transport_type == TransportType.STDIO
        assert isinstance(server._transport, StdioTransport)
    
    def test_init_sse(self, sse_config):
        """Test initialization with SSE transport."""
        server = MCPServer("test-sse", sse_config)
        assert server.transport_type == TransportType.SSE
        assert isinstance(server._transport, SSETransport)
    
    def test_init_invalid_transport(self):
        """Test initialization with invalid transport."""
        with pytest.raises(ValueError, match="Unsupported transport type"):
            MCPServer("test-invalid", {"transport_type": "invalid"})
    
    def test_stdio_missing_command(self):
        """Test STDIO missing command."""
        with pytest.raises(ValueError, match="STDIO transport requires 'command'"):
            MCPServer("test-stdio", {"transport_type": "stdio"})
    
    def test_sse_missing_url(self):
        """Test SSE missing URL."""
        with pytest.raises(ValueError, match="SSE transport requires 'url'"):
            MCPServer("test-sse", {"transport_type": "sse"})
    
    @pytest.mark.asyncio
    async def test_connect_stdio_success(self, stdio_config):
        """Test successful STDIO connection."""
        server = MCPServer("test-stdio", stdio_config)
        
        # Mock the transport.connect method
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        server._transport.connect = AsyncMock(return_value=(mock_read, mock_write))
        
        # Mock ClientSession
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=[])
        mock_session.list_resources = AsyncMock(return_value=[])
        mock_session.list_prompts = AsyncMock(return_value=[])
        
        with patch("agent_c.toolsets.mcp_server.ClientSession", return_value=mock_session):
            # Test connection
            result = await server.connect()
            assert result is True
            assert server.connected is True
            
            # Verify methods were called
            server._transport.connect.assert_called_once()
            mock_session.initialize.assert_called_once()
            mock_session.list_tools.assert_called_once()
            mock_session.list_resources.assert_called_once()
            mock_session.list_prompts.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_sse_success(self, sse_config):
        """Test successful SSE connection."""
        server = MCPServer("test-sse", sse_config)
        
        # Mock the transport.connect method
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        server._transport.connect = AsyncMock(return_value=(mock_read, mock_write))
        
        # Mock ClientSession
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=[])
        mock_session.list_resources = AsyncMock(return_value=[])
        mock_session.list_prompts = AsyncMock(return_value=[])
        
        with patch("agent_c.toolsets.mcp_server.ClientSession", return_value=mock_session):
            # Test connection
            result = await server.connect()
            assert result is True
            assert server.connected is True
            
            # Verify methods were called
            server._transport.connect.assert_called_once()
            mock_session.initialize.assert_called_once()
            mock_session.list_tools.assert_called_once()
            mock_session.list_resources.assert_called_once()
            mock_session.list_prompts.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure_retries(self, stdio_config):
        """Test connection failures with retries."""
        server = MCPServer("test-retry", stdio_config)
        
        # Make the transport.connect method fail the first two times
        server._transport.connect = AsyncMock(side_effect=[
            ConnectionError("First failure"),
            ConnectionError("Second failure"),
            (AsyncMock(), AsyncMock())
        ])
        
        # Mock ClientSession
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=[])
        mock_session.list_resources = AsyncMock(return_value=[])
        mock_session.list_prompts = AsyncMock(return_value=[])
        
        with patch("agent_c.toolsets.mcp_server.ClientSession", return_value=mock_session), \
             patch("agent_c.toolsets.mcp_server.asyncio.sleep", AsyncMock()):
            # Test connection with retries
            result = await server.connect(max_retries=3, retry_delay=0.1)
            assert result is True
            assert server.connected is True
            
            # Verify connect was called three times
            assert server._transport.connect.call_count == 3
    
    @pytest.mark.asyncio
    async def test_discover_tools(self, stdio_config):
        """Test tool discovery."""
        server = MCPServer("test-tools", stdio_config)
        server.session = AsyncMock()
        server.connected = True
        
        # Mock tool data
        tool_data = [
            ("tools", [
                MagicMock(name="tool1", description="Tool 1", inputSchema={"type": "object"}),
                MagicMock(name="tool2", description="Tool 2", inputSchema={"type": "object"})
            ])
        ]
        server.session.list_tools = AsyncMock(return_value=tool_data)
        
        # Test tool discovery
        tools = await server.discover_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools
        assert tools["tool1"]["description"] == "Tool 1"
        assert tools["tool2"]["description"] == "Tool 2"
    
    @pytest.mark.asyncio
    async def test_discover_resources(self, stdio_config):
        """Test resource discovery."""
        server = MCPServer("test-resources", stdio_config)
        server.session = AsyncMock()
        server.connected = True
        
        # Mock resource data
        resource_data = [
            ("resources", [
                MagicMock(uri="resource://one", mimeType="text/plain"),
                MagicMock(uri="resource://two", mimeType="application/json")
            ])
        ]
        server.session.list_resources = AsyncMock(return_value=resource_data)
        
        # Test resource discovery
        resources = await server.discover_resources()
        assert len(resources) == 2
        assert "resource://one" in resources
        assert "resource://two" in resources
        assert resources["resource://one"]["mimeType"] == "text/plain"
        assert resources["resource://two"]["mimeType"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_read_resource(self, stdio_config):
        """Test reading a resource."""
        server = MCPServer("test-read", stdio_config)
        server.session = AsyncMock()
        server.connected = True
        server.resources = {"resource://test": {"uri": "resource://test", "mimeType": "text/plain"}}
        
        # Mock resource read result
        mock_result = MagicMock(content="Resource content", mimeType="text/plain")
        server.session.read_resource = AsyncMock(return_value=mock_result)
        
        # Test resource reading
        content, mime_type = await server.read_resource("resource://test")
        assert content == "Resource content"
        assert mime_type == "text/plain"
        server.session.read_resource.assert_called_once_with("resource://test")
    
    @pytest.mark.asyncio
    async def test_call_tool(self, stdio_config):
        """Test calling a tool."""
        server = MCPServer("test-call", stdio_config)
        server.session = AsyncMock()
        server.connected = True
        server.tools = {"test_tool": {"name": "test_tool", "description": "Test tool", "schema": {}}}
        
        # Mock tool call result
        server.session.call_tool = AsyncMock(return_value="Tool result")
        
        # Test tool calling
        result = await server.call_tool("test_tool", {"arg": "value"})
        assert result == "Tool result"
        server.session.call_tool.assert_called_once_with("test_tool", {"arg": "value"})
    
    @pytest.mark.asyncio
    async def test_get_prompt(self, stdio_config):
        """Test getting a prompt."""
        server = MCPServer("test-prompt", stdio_config)
        server.session = AsyncMock()
        server.connected = True
        server.prompts = {"test_prompt": {"name": "test_prompt", "description": "Test prompt", "parameters": {}}}  
        
        # Mock prompt result
        mock_result = MagicMock(prompt="Prompt text")
        server.session.get_prompt = AsyncMock(return_value=mock_result)
        
        # Test getting prompt
        result = await server.get_prompt("test_prompt", {"arg": "value"})
        assert result == "Prompt text"
        server.session.get_prompt.assert_called_once_with("test_prompt", {"arg": "value"})
    
    @pytest.mark.asyncio
    async def test_format_tool_result_string(self, stdio_config):
        """Test formatting string tool results."""
        server = MCPServer("test-format", stdio_config)
        assert server._format_tool_result("string result") == "string result"
    
    @pytest.mark.asyncio
    async def test_format_tool_result_primitive(self, stdio_config):
        """Test formatting primitive tool results."""
        server = MCPServer("test-format", stdio_config)
        assert server._format_tool_result(123) == "123"
        assert server._format_tool_result(1.23) == "1.23"
        assert server._format_tool_result(True) == "True"
    
    @pytest.mark.asyncio
    async def test_format_tool_result_complex(self, stdio_config):
        """Test formatting complex tool results."""
        server = MCPServer("test-format", stdio_config)
        data = {"key": "value", "list": [1, 2, 3]}
        expected = json.dumps(data, indent=2, ensure_ascii=False)
        assert server._format_tool_result(data) == expected