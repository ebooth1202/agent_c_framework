# Tool Debugger - Updated with Centralized Configuration

## Overview

The `ToolDebugger` class has been enhanced to automatically load configuration files from a centralized location, making it easier to use across different tools and projects.

## New Features

### 1. **Centralized .env Loading**
- Automatically loads `.env` file from `\path\agent_c\.env`
- Makes environment variables available to all tools
- Optional dependency on `python-dotenv`

### 2. **Centralized .local_workspaces.json Loading**  
- Loads workspace configuration from `\path\agent_c\.local_workspaces.json`
- No longer requires the file to be in the tool_debugger directory
- Better organization of workspace configurations

### 3. **Auto-Detection of Agent C Base Path**
- Automatically finds the agent_c base directory
- Supports custom path specification
- Fallback mechanisms for different directory structures

## Installation

### Required Dependencies
```bash
pip install agent_c  # (already installed)
```

### Optional Dependencies
```bash
pip install python-dotenv  # For .env file loading
```

## Usage

### Basic Usage (Recommended)
```python
from debug_tool import ToolDebugger

# Auto-detects agent_c base path and loads configurations
tester = ToolDebugger(log_level=logging.INFO, init_local_workspaces=False)
```

### With Custom Base Path
```python
tester = ToolDebugger(
    log_level=logging.INFO, 
    init_local_workspaces=False,
    agent_c_base_path=r"C:\your\custom\path"
)
```

### Configuration Loading
The debugger automatically:

1. **Finds agent_c base directory** by:
   - Using provided `agent_c_base_path` if specified
   - Auto-detecting by traversing up directory tree looking for "agent_c" folder
   - Looking for directories containing `.env` or `.local_workspaces.json` files
   - Falling back to current working directory if no path is provided

2. **Loads .env file** from `{agent_c_base_path}/.env`
   - Requires `python-dotenv` package
   - Logs warning if file exists but package not installed
   - Silently skips if file doesn't exist

3. **Loads .local_workspaces.json** from `{agent_c_base_path}/.local_workspaces.json`
   - Only when `init_local_workspaces=True`
   - Logs info if file doesn't exist
   - Adds workspaces to the tool environment

## Example Configuration Files

### .env File (`C:\...\...\..\agent_c\.env`)
```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
FLASHDOCS_API_KEY=your_flashdocs_key_here
WEATHER_API_KEY=your_weather_key_here

# Database configurations
DATABASE_URL=your_database_url_here

# Other environment variables
DEBUG=True
LOG_LEVEL=INFO
```

### .local_workspaces.json (`path\agent_c\.local_workspaces.json`)
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

## Example Usage

```python
import asyncio
import logging
from debug_tool import ToolDebugger

async def test_weather_tool():
    # Create debugger with auto-loading
    tester = ToolDebugger(log_level=logging.INFO, init_local_workspaces=False)
    
    # Print configuration info
    print(f"Agent C base path: {tester.agent_c_base_path}")
    
    # Setup tool (API keys loaded from .env automatically)
    await tester.setup_tool(
        tool_import_path='agent_c_tools.WeatherTools',
        tool_opts={}  # Can still override or add additional config
    )
    
    # Test the tool
    result = await tester.run_tool_test(
        tool_name='get_current_weather',
        tool_params={'location_name': 'New York'},
        tool_context={'key': 'value'}  # Optional context, can be used for passing additional data
    )
    
    # Process results
    content = tester.extract_content_from_results(result)
    print("Weather data:", content)

if __name__ == "__main__":
    asyncio.run(test_weather_tool())
```

## Troubleshooting

### Common Issues

1. **Cannot find agent_c base path**
   - Specify path explicitly: `ToolDebugger(agent_c_base_path=r"C:\your\path")`
   - Check that the directory exists and contains expected files

2. **.env file not loading**
   - Install python-dotenv: `pip install python-dotenv`
   - Check that .env file exists in the correct location
   - Verify file permissions

3. **Workspaces not loading**
   - Check that `.local_workspaces.json` exists and has correct format
   - Verify workspace paths exist and are accessible
   - Check log messages for specific errors

4. **Tools not finding API keys**
   - Verify .env file is loaded (check log messages)
   - Ensure environment variable names match what tools expect
   - Can still override in tool_opts if needed
