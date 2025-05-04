# src/agent_c_api/tests/v2/models/test_tool_models.py
import pytest
from agent_c_api.api.v2.models.tool_models import (
    ToolParameter, ToolInfo, ToolCategory, ToolsList,
    SessionTools, ToolsUpdate, ToolCall, ToolResult
)

def test_tool_parameter():
    # Test with minimal fields
    param = ToolParameter(
        name="query",
        type="string",
        description="Search query"
    )
    assert param.name == "query"
    assert param.type == "string"
    assert param.description == "Search query"
    assert param.required is False
    assert param.default is None
    
    # Test with all fields
    param = ToolParameter(
        name="max_results",
        type="integer",
        description="Maximum number of results",
        required=True,
        default=10
    )
    assert param.name == "max_results"
    assert param.type == "integer"
    assert param.description == "Maximum number of results"
    assert param.required is True
    assert param.default == 10

def test_tool_info():
    # Test with minimal fields
    tool = ToolInfo(
        id="search",
        name="Web Search",
        description="Search the web for information",
        category="Information"
    )
    assert tool.id == "search"
    assert tool.name == "Web Search"
    assert tool.description == "Search the web for information"
    assert tool.category == "Information"
    assert tool.parameters == []
    assert tool.examples == []
    
    # Test with all fields
    param = ToolParameter(name="query", type="string", description="Search query")
    tool = ToolInfo(
        id="calculator",
        name="Calculator",
        description="Perform mathematical calculations",
        category="Utilities",
        parameters=[param],
        examples=["calculator 2 + 2", "calculator sin(30)"]
    )
    assert tool.id == "calculator"
    assert tool.name == "Calculator"
    assert tool.description == "Perform mathematical calculations"
    assert tool.category == "Utilities"
    assert len(tool.parameters) == 1
    assert tool.parameters[0].name == "query"
    assert tool.examples == ["calculator 2 + 2", "calculator sin(30)"]

def test_tool_category():
    # Create a tool for the category
    tool = ToolInfo(
        id="search",
        name="Web Search",
        description="Search the web for information",
        category="Information"
    )
    
    # Test category
    category = ToolCategory(
        name="Information",
        description="Tools for finding information",
        tools=[tool]
    )
    assert category.name == "Information"
    assert category.description == "Tools for finding information"
    assert len(category.tools) == 1
    assert category.tools[0].id == "search"

def test_tools_list():
    # Create tool and category
    tool = ToolInfo(
        id="search",
        name="Web Search",
        description="Search the web for information",
        category="Information"
    )
    category = ToolCategory(
        name="Information",
        description="Tools for finding information",
        tools=[tool]
    )
    
    # Test tools list
    tools_list = ToolsList(categories=[category])
    assert len(tools_list.categories) == 1
    assert tools_list.categories[0].name == "Information"
    assert len(tools_list.categories[0].tools) == 1

def test_session_tools():
    # Test session tools
    tools = SessionTools(
        enabled_tools=["search", "calculator"],
        available_tools=["weather", "translator"]
    )
    assert tools.enabled_tools == ["search", "calculator"]
    assert tools.available_tools == ["weather", "translator"]

def test_tools_update():
    # Test tools update
    update = ToolsUpdate(enabled_tools=["search", "calculator"])
    assert update.enabled_tools == ["search", "calculator"]

def test_tool_call():
    # Test tool call
    call = ToolCall(
        tool_id="calculator",
        parameters={"expression": "2 + 2"}
    )
    assert call.tool_id == "calculator"
    assert call.parameters == {"expression": "2 + 2"}

def test_tool_result():
    # Test successful result
    result = ToolResult(
        tool_id="calculator",
        success=True,
        result=4
    )
    assert result.tool_id == "calculator"
    assert result.success is True
    assert result.result == 4
    assert result.error is None
    
    # Test error result
    result = ToolResult(
        tool_id="calculator",
        success=False,
        result=None,
        error="Invalid expression"
    )
    assert result.tool_id == "calculator"
    assert result.success is False
    assert result.result is None
    assert result.error == "Invalid expression"