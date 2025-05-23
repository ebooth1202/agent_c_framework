# Tool Debugger Guide

## Manual Debugging and Testing for Agent C Tools

The **Tool Debugger** is an enhanced testing framework that allows you to manually debug and test Agent C tools with real configurations and API calls.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation and Setup](#installation-and-setup)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Configuration Management](#configuration-management)
7. [Debugging Workflows](#debugging-workflows)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

---

## Overview

### **What is Tool Debugger?**

Tool Debugger is a **standalone testing harness** that allows you to:

- **Load and test any Agent C tool** without a full agent setup
- **Use real configurations** (.env files, workspace configs)
- **Make actual API calls** to validate tool functionality
- **Debug tool behavior** interactively
- **Validate tool registration** and schema definitions

### **When to Use Tool Debugger**

- 🔧 **Manual testing** during development
- 🐛 **Debugging tool issues** 
- ✅ **Validating tool functionality** before deployment
- 📋 **Exploring tool capabilities** and parameters
- 🧪 **Integration testing** in automated test suites

---

## Features

### **🎯 Core Features**

- **Automatic Configuration Loading** - Loads .env and .local_workspaces.json from centralized location
- **Dynamic Tool Import** - Import any tool class by name
- **Real API Calls** - Tests with actual external services
- **Tool Introspection** - Examine tool schemas, methods, and parameters
- **Result Processing** - Extract and parse tool results
- **Workspace Support** - Full workspace functionality when needed

### **🚀 Enhanced Features**

- **Auto-Detection** - Finds agent_c base directory automatically
- **Centralized Config** - Loads configurations from `C:\Users\justj\PycharmProjects\agent_c\`
- **Environment Variables** - Automatic .env file loading with python-dotenv
- **Error Handling** - Graceful handling of missing files and configurations
- **Logging** - Comprehensive logging for debugging

---

## Installation and Setup

### **Required Dependencies**

```bash
# Core dependencies (should already be installed)
pip install agent_c

# Optional but recommended
pip install python-dotenv  # For .env file loading
```

### **Configuration Files**

Create these files in your agent_c base directory:

#### **.env** (`C:\path\agent_c\.env`)
```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
WEATHER_API_KEY=your_weather_key_here
FLASHDOCS_API_KEY=your_flashdocs_key_here

# Database configurations  
DATABASE_URL=your_database_url_here

# Other settings
DEBUG=True
LOG_LEVEL=INFO
```

#### **.local_workspaces.json** (`C:\path\agent_c\.local_workspaces.json`)
```json
{
  "local_workspaces": [
    {
      "workspace_name": "Documents",
      "workspace_root": "C:\\Documents",
      "description": "Personal documents workspace"
    },
    {
      "workspace_name": "Projects",
      "workspace_root": "C:\\Projects", 
      "description": "Development projects workspace"
    }
  ]
}
```

---

## Basic Usage

### **Simple Tool Testing**

```python
import asyncio
import logging
from debug_tool import ToolDebugger

async def test_weather_tool():
    # Create debugger - automatically loads configurations
    debugger = ToolDebugger(log_level=logging.INFO, init_local_workspaces=False)
    
    # Setup the weather tool
    await debugger.setup_tool(
        tool_import_path='agent_c_tools.WeatherTools',
        tool_opts={}  # API keys loaded from .env automatically
    )
    
    # Test the tool
    results = await debugger.run_tool_test(
        tool_name='get_current_weather',
        tool_params={'location_name': 'New York'}
    )
    
    # Process results
    content = debugger.extract_content_from_results(results)
    print("Weather data:", content)

if __name__ == "__main__":
    asyncio.run(test_weather_tool())
```

### **Tool Introspection**

```python
async def explore_tool():
    debugger = ToolDebugger()
    await debugger.setup_tool('agent_c_tools.WeatherTools', {})
    
    # Get available tool methods
    tool_names = debugger.get_available_tool_names()
    print("Available tools:", tool_names)
    
    # Print detailed tool information
    debugger.print_tool_info()

asyncio.run(explore_tool())
```

---

## Advanced Features

### **Custom Configuration Path**

```python
# Specify custom agent_c base directory
debugger = ToolDebugger(
    log_level=logging.INFO,
    init_local_workspaces=False,
    agent_c_base_path=r"C:\\your\\custom\\path"
)
```

### **Workspace-Enabled Tools**

```python
# For tools that require workspace functionality
debugger = ToolDebugger(
    log_level=logging.INFO,
    init_local_workspaces=True  # Enables workspace support
)

await debugger.setup_tool('agent_c_tools.WorkspaceTools', {})
```

### **Tool Configuration Override**

```python
# Override or add configuration
await debugger.setup_tool(
    tool_import_path='agent_c_tools.DatabaseTools',
    tool_opts={
        'DATABASE_URL': 'custom_database_url',  # Override .env value
        'MAX_CONNECTIONS': 10,                  # Add additional config
        'custom_setting': 'value'               # Tool-specific settings
    }
)
```

### **Multiple Tools Testing**

```python
async def test_multiple_tools():
    debugger = ToolDebugger()
    
    # Setup multiple tools
    await debugger.setup_tool('agent_c_tools.WeatherTools', {})
    await debugger.setup_tool('agent_c_tools.WebSearchTools', {})
    
    # Test weather
    weather_result = await debugger.run_tool_test(
        'get_current_weather', 
        {'location_name': 'London'}
    )
    
    # Test web search  
    search_result = await debugger.run_tool_test(
        'web_search',
        {'query': 'Agent C tools'}
    )
    
    print("Weather:", debugger.extract_content_from_results(weather_result))
    print("Search:", debugger.extract_content_from_results(search_result))
```

---

## Configuration Management

### **Automatic Configuration Loading**

The debugger automatically:

1. **Finds agent_c base directory** by:
   - Using provided `agent_c_base_path` if specified
   - Auto-detecting by looking for "agent_c" folder name
   - Finding directories with .env or .local_workspaces.json files
   - Falling back to hardcoded path

2. **Loads .env file** from `{agent_c_base}/env`
   - Requires python-dotenv package
   - Logs warning if file exists but package not installed
   - Silently continues if file doesn't exist

3. **Loads workspace configuration** from `{agent_c_base}/.local_workspaces.json`
   - Only when `init_local_workspaces=True`
   - Adds workspaces to tool environment
   - Logs info about loaded workspaces

### **Configuration Priority**

Configuration values are applied in this order (later overrides earlier):

1. **System environment variables**
2. **.env file values** (loaded by debugger)
3. **tool_opts values** (passed to setup_tool)

```python
# Example: DATABASE_URL priority
# 1. System env: DATABASE_URL=system_value
# 2. .env file: DATABASE_URL=env_file_value  
# 3. tool_opts: {'DATABASE_URL': 'override_value'}
# Result: tool gets 'override_value'
```

### **Configuration Validation**

```python
async def validate_config():
    debugger = ToolDebugger()
    
    # Print configuration info
    print(f"Agent C base path: {debugger.agent_c_base_path}")
    
    # Check if files exist
    import os
    env_exists = os.path.exists(os.path.join(debugger.agent_c_base_path, '.env'))
    ws_exists = os.path.exists(os.path.join(debugger.agent_c_base_path, '.local_workspaces.json'))
    
    print(f"Environment file loaded: {env_exists}")
    print(f"Workspaces config exists: {ws_exists}")
```

---

## Debugging Workflows

### **1. Initial Tool Validation**

```python
async def validate_new_tool():
    "Basic validation workflow for a new tool."
    debugger = ToolDebugger(log_level=logging.DEBUG)  # Verbose logging
    
    try:
        # Step 1: Setup tool
        await debugger.setup_tool('agent_c_tools.YourNewTool', {})
        print("✅ Tool setup successful")
        
        # Step 2: Check tool registration
        available_tools = debugger.get_available_tool_names()
        print(f"Available tools: {available_tools}")
        
        # Step 3: Examine tool details
        debugger.print_tool_info()
        
        # Step 4: Test basic functionality
        results = await debugger.run_tool_test(
            'your_tool_method',
            {'required_param': 'test_value'}
        )
        
        content = debugger.extract_content_from_results(results)
        print(f"Tool output: {content}")
        
    except Exception as e:
        print(f"❌ Tool validation failed: {e}")
```

### **2. Parameter Testing**

```python
async def test_tool_parameters():
    "Test different parameter combinations."
    debugger = ToolDebugger()
    await debugger.setup_tool('agent_c_tools.YourTool', {})
    
    # Test cases with different parameters
    test_cases = [
        {'param1': 'value1', 'param2': 'value2'},
        {'param1': 'different_value'},
        {},  # Empty parameters
        {'param1': 'value1', 'unexpected_param': 'value'}  # Extra parameters
    ]
    
    for i, params in enumerate(test_cases):
        print(f"Test case {i+1}: {params}")
        try:
            results = await debugger.run_tool_test('your_method', params)
            content = debugger.extract_content_from_results(results)
            print(f"Result: {content[:100]}...")  # First 100 chars
        except Exception as e:
            print(f"Error: {e}")
```

### **3. Error Scenario Testing**

```python
async def test_error_scenarios():
    "Test how tool handles various error conditions."
    debugger = ToolDebugger()
    await debugger.setup_tool('agent_c_tools.YourTool', {})
    
    # Test invalid inputs
    error_test_cases = [
        {'param': None},
        {'param': ''},
        {'param': 'invalid_value'},
        {'param': 'extremely_long_value' * 1000}
    ]
    
    for case in error_test_cases:
        results = await debugger.run_tool_test('your_method', case)
        content = debugger.extract_content_from_results(results)
        
        if content.startswith("Error:"):
            print(f"✅ Proper error handling for {case}: {content}")
        else:
            print(f"⚠️  No error for {case}: {content}")
```

### **4. Performance Testing**

```python
import time

async def test_tool_performance():
    "Basic performance testing."
    debugger = ToolDebugger()
    await debugger.setup_tool('agent_c_tools.YourTool', {})
    
    # Test response times
    test_params = {'param': 'standard_test_value'}
    times = []
    
    for i in range(5):
        start_time = time.time()
        results = await debugger.run_tool_test('your_method', test_params)
        end_time = time.time()
        
        duration = end_time - start_time
        times.append(duration)
        print(f"Run {i+1}: {duration:.2f} seconds")
    
    avg_time = sum(times) / len(times)
    print(f"Average response time: {avg_time:.2f} seconds")
```

---

## Troubleshooting

### **Common Issues and Solutions**

#### **1. Tool Import Errors**

```
ImportError: No module named 'your_tool_module'
```

**Solution:**
```python
# Check the import path
await debugger.setup_tool(
    tool_import_path='agent_c_tools.CorrectToolName',  # Exact class name
    tool_opts={}
)
```

#### **2. Configuration Not Loading**

```
API keys not found, tools failing with authentication errors
```

**Solutions:**
```python
# Check file locations
debugger = ToolDebugger()
print(f"Looking for config in: {debugger.agent_c_base_path}")

# Specify path explicitly
debugger = ToolDebugger(agent_c_base_path=r"C:\\correct\\path\\to\\agent_c")

# Override in tool_opts
await debugger.setup_tool('agent_c_tools.YourTool', {
    'API_KEY': 'your_api_key_here'
})
```

#### **3. Workspace Errors**

```
Workspace-related tools failing
```

**Solution:**
```python
# Enable workspace initialization
debugger = ToolDebugger(init_local_workspaces=True)

# Check workspace configuration
import os
ws_file = os.path.join(debugger.agent_c_base_path, '.local_workspaces.json')
if os.path.exists(ws_file):
    print("Workspace config found")
else:
    print("Create .local_workspaces.json file")
```

#### **4. Tool Not Found**

```
Tool method not available in get_available_tool_names()
```

**Solutions:**
```python
# Check tool registration
debugger.print_tool_info()  # Shows all registered tools and methods

# Verify tool class name
await debugger.setup_tool('agent_c_tools.ExactClassName', {})

# Check for tool naming conflicts
available = debugger.get_available_tool_names()
print("Available tools:", available)
```

### **Debugging Tips**

1. **Use verbose logging**: `ToolDebugger(log_level=logging.DEBUG)`
2. **Check configuration paths**: Print `debugger.agent_c_base_path`
3. **Validate tool registration**: Use `debugger.print_tool_info()`
4. **Test incrementally**: Start with simple parameters, add complexity
5. **Check network connectivity**: Many tools require internet access

---

## Examples

### **Weather Tool Debugging**

```python
import asyncio
import logging
from debug_tool import ToolDebugger

async def debug_weather_tool():
    # Create debugger with verbose logging
    debugger = ToolDebugger(log_level=logging.INFO)
    
    print(f"Configuration loaded from: {debugger.agent_c_base_path}")
    
    # Setup weather tool
    await debugger.setup_tool('agent_c_tools.WeatherTools', {})
    
    # Check what's available
    print("\\nAvailable tools:", debugger.get_available_tool_names())
    
    # Test different locations
    locations = ['New York', 'London', 'Tokyo', 'InvalidLocation123']
    
    for location in locations:
        print(f"\\n--- Testing location: {location} ---")
        results = await debugger.run_tool_test(
            'get_current_weather',
            {'location_name': location}
        )
        
        content = debugger.extract_content_from_results(results)
        
        if content.startswith('Error'):
            print(f"❌ Error: {content}")
        else:
            # Parse JSON and show key info
            structured = debugger.extract_structured_content(results)
            if structured and 'currently' in structured:
                temp = structured['currently'].get('current_temperature', 'N/A')
                desc = structured['currently'].get('description', 'N/A')
                print(f"✅ Success: {temp}°F, {desc}")
            else:
                print(f"✅ Raw result: {content[:100]}...")

if __name__ == "__main__":
    asyncio.run(debug_weather_tool())
```

### **Database Tool Debugging**

```python
async def debug_database_tool():
    debugger = ToolDebugger(log_level=logging.DEBUG)
    
    # Setup with custom database URL
    await debugger.setup_tool('agent_c_tools.DatabaseTools', {
        'DATABASE_URL': 'postgresql://user:pass@localhost/testdb'
    })
    
    # Test connection
    results = await debugger.run_tool_test(
        'test_connection',
        {}
    )
    
    content = debugger.extract_content_from_results(results)
    print(f"Connection test: {content}")
    
    # Test simple query
    if not content.startswith('Error'):
        query_results = await debugger.run_tool_test(
            'execute_query',
            {'query': 'SELECT 1 as test_value'}
        )
        
        query_content = debugger.extract_content_from_results(query_results)
        print(f"Query result: {query_content}")
```

### **Multi-Tool Integration Testing**

```python
async def test_tool_integration():
    """Test multiple tools working together."""
    debugger = ToolDebugger()
    
    # Setup multiple tools
    await debugger.setup_tool('agent_c_tools.WeatherTools', {})
    await debugger.setup_tool('agent_c_tools.WebSearchTools', {})
    
    # Get weather for a location
    weather_results = await debugger.run_tool_test(
        'get_current_weather',
        {'location_name': 'San Francisco'}
    )
    
    weather_content = debugger.extract_content_from_results(weather_results)
    
    if not weather_content.startswith('Error'):
        # Search for weather-related information
        search_results = await debugger.run_tool_test(
            'web_search',
            {'query': 'San Francisco weather forecast'}
        )
        
        search_content = debugger.extract_content_from_results(search_results)
        
        print("Weather data:", weather_content[:200])
        print("Search results:", search_content[:200])
```

---

## Best Practices

### **Development Workflow** 🔄

1. **Start Simple** - Test basic functionality first
2. **Add Complexity** - Gradually test more complex scenarios  
3. **Test Edge Cases** - Invalid inputs, error conditions
4. **Validate Configuration** - Ensure settings are loaded correctly
5. **Document Findings** - Keep notes on what works and what doesn't

### **Configuration Management** ⚙️

1. **Use .env files** - Keep API keys and settings centralized
2. **Version control .env.example** - Template for other developers
3. **Test with different configs** - Validate tools work with various settings
4. **Override when needed** - Use tool_opts for test-specific configuration

### **Debugging Strategies** 🐛

1. **Use verbose logging** - `log_level=logging.DEBUG` for detailed info
2. **Test incrementally** - Add one parameter at a time
3. **Check tool registration** - Use `debugger.print_tool_info()`
4. **Validate inputs** - Ensure parameters match tool expectations
5. **Handle errors gracefully** - Always wrap in try/except blocks

The Tool Debugger is your **primary tool for developing and validating Agent C tools**. Use it extensively during development to ensure your tools work correctly before deployment! 🛠️✅
