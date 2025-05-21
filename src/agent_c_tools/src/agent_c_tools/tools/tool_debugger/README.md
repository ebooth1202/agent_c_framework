# Agent-C Tool Debugger
A utility for testing and debugging Agent-C tools without a full agent setup.

## Overview
The `ToolDebugger` allows you to:
- Load and test any Agent-C tool independently
- Configure tools with custom parameters
- Handle tools with dependencies (like workspace requirements)
- Extract and parse tool results
- Debug tool issues without a full agent setup

## Basic Usage

Here's a simple example testing the WeatherTools:

```python
import asyncio
import logging
from debug_tool import ToolDebugger

async def run_example():
    # Create the tool debugger
    tester = ToolDebugger(log_level=logging.INFO)
    
    # Setup a tool
    await tester.setup_tool(
        tool_import_path='agent_c_tools.WeatherTools',
        tool_opts={}
    )
    
    # Show available tools and methods
    tester.print_tool_info()
    
    # Get tool names for function calls
    tool_names = tester.get_available_tool_names()
    print(f"Available tool names: {tool_names}")
    
    # Run a tool test
    result = await tester.run_tool_test(
        tool_name='get_current_weather',
        tool_params={'location_name': 'New York'}
    )
    
    # Extract and display the results
    content = tester.extract_content_from_results(result)
    print("Raw content:", content)
    
    # Parse JSON results if available
    structured_content = tester.extract_structured_content(result)
    if structured_content:
        print("Current temperature:", 
              structured_content.get('currently', {}).get('current_temperature'))

if __name__ == "__main__":
    asyncio.run(run_example())
```

## Workspace Configuration

For tools that require workspaces (like `MarkdownToHtmlReportTools`), create a `.local_workspaces.json` file in the same directory as your `debug_tool.py`:

```json
{
  "local_workspaces": [
    {
      "name": "robots",
      "workspace_path": "C:\\path\\to\\your\\workspace",
      "description": "Your workspace description"
    }
  ]
}
```

The debugger will automatically load these workspaces when `init_local_workspaces=True` (default).

## Testing Tools with Dependencies

Some tools have dependencies (like `WorkspaceTools`). The debugger will automatically handle these dependencies:

```python
# Create debugger with workspace support enabled
tester = ToolDebugger(log_level=logging.INFO)

# Setup the main tool - dependencies will be auto-loaded
await tester.setup_tool(
    tool_import_path='agent_c_tools.MarkdownToHtmlReportTools',
    tool_opts={}
)

# You can now see both the main tool and its dependencies
tester.print_tool_info()

# Run a test using the tool
result = await tester.run_tool_test(
    tool_name='generate_md_viewer',
    tool_params={
        "workspace": "robots",
        "file_path": "requirements",
        "output_filename": "test_viewer.html",
        "title": "Markdown Viewer Test"
    }
)
```

## Tool names / Function Names
- The tool names are derived from the function names in the imported module, e.g., `get_current_weather` from `WeatherTools`.
- If a tool has `use_prefix=False` just call the function name.
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs, name="markdown_viewer", use_prefix=False)
...
async def generate_md_viewer(self, **kwargs) -> str:
...
```
- In this case, just use `generate_md_viewer`
```python

# Run a tool call, pass in parameters.  Format of the tool name is <toolset_name>_<function_name>
result = await tester.run_tool_test(
    tool_name='generate_md_viewer',
    tool_params={"workspace": "robots",
                 "file_path": "requirements",
                 "output_filename": "test_viewer.html",
                 "title": "Markdown Viewer Smoke‑Test", }
    )
```

- If the tool has `use_prefix=True` (default) or no use_prefix set, the function name will be prefixed with the toolset name.
```python
api_key = 'SuperSecretKey'
await tester.setup_tool(tool_import_path='agent_c_tools.FlashDocsTools',
                        tool_opts={'FLASHDOCS_API_KEY': api_key})

# Run a tool call, pass in parameters.  
result = await tester.run_tool_test(
    tool_name='flash_docs_outline_to_powerpoint',
    tool_params={"outline": ["# intro", "# slide 2"],
                 "presentation_name": "Smoke‑Test", }
)
```
- Notice the use of the tool_name of `flash_docs_outline_to_powerpoint` instead of `outline_to_powerpoint`

## Key Methods

- `setup_tool(tool_import_path, tool_opts)`: Imports and initializes a tool
- `run_tool_test(tool_name, tool_params)`: Executes a tool function with parameters
- `print_tool_info()`: Displays detailed information about loaded tools
- `get_available_tool_names()`: Returns a list of available tool function names
- `extract_content_from_results(results)`: Extracts content from the tool results
- `extract_structured_content(results)`: Parses JSON content from results

## Configuration Options

When creating a `ToolDebugger` instance:

- `log_level`: Sets the logging level (default: `logging.INFO`)
- `init_local_workspaces`: Whether to initialize local workspaces (default: `True`)
  - Set to `False` when testing tools that don't need workspaces
  - A warning will appear if a tool requires workspaces but `init_local_workspaces=False`

## Troubleshooting

1. **Import errors**: Ensure agent_c and related packages are in your Python path
2. **Workspace errors**: Check your `.local_workspaces.json` configuration
3. **Dependency warnings**: If you see warnings about missing dependencies, ensure `init_local_workspaces=True`
4. **Extraction errors**: Some tools may return results in non-standard formats

## Running the Examples

The repository includes two example files:

- `example.py`: Tests WeatherTools (no workspace dependencies)
- `example2.py`: Tests MarkdownToHtmlReportTools (requires workspaces)

Run these with:

```
python example.py
python example2.py
```