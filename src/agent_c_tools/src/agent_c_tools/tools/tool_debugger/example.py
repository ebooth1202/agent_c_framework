import asyncio
import logging
import os
from debug_tool import ToolDebugger


async def run_example():
    """Simple example of how to use the ToolDebugger with centralized config loading"""
    # Create the tool tester
    # The debugger will automatically:
    # 1. Auto-detect the agent_c base path
    # 2. Load .local_workspaces.json from agent_c\.local_workspaces.json
    # 3. Load .env from agent_c\.env
    
    # You can also specify a custom agent_c base path:
    # tester = ToolDebugger(log_level=logging.INFO, init_local_workspaces=False, 
    #                      agent_c_base_path=r"C:\your\custom\path")
    
    tester = ToolDebugger(log_level=logging.INFO, init_local_workspaces=False)
    
    # Print some info about loaded configuration
    print(f"\nAgent C base path: {tester.agent_c_base_path}")
    print(f"Environment variables loaded from .env: {os.path.exists(os.path.join(tester.agent_c_base_path, '.env'))}")
    print(f"Local workspaces config exists: {os.path.exists(os.path.join(tester.agent_c_base_path, '.local_workspaces.json'))}")

    # Setup a weather tool as a simple example
    # Since .env is loaded, any API keys in the .env file will be available
    # tool_opts can override or add additional configuration
    await tester.setup_tool(tool_import_path='agent_c_tools.WeatherTools',
                            tool_opts={})

    # Get tool info
    tester.print_tool_info()

    # Get the correct tool names
    tool_names = tester.get_available_tool_names()
    print(f"\nAvailable tool names: {tool_names}")

    # Run a tool call, pass in parameters.  Format of the tool name is <toolset_name>_<function_name>
    result = await tester.run_tool_test(
        tool_name='get_current_weather',
        tool_params={'location_name': 'New York'}
    )

    # Get raw content (JSON string)
    content = tester.extract_content_from_results(result)
    if content:
        print("Raw content:", content)

        # Detect content format
        format_detected = tester.detect_content_format(result)
        print(f"Detected format: {format_detected}")

        # Get structured content with auto-detection (recommended) - The below code is simply multiple ways of extracting content from a tool call
        # This supports legacy tools that return JSON.dumps, as well as the newer recommended approach that tools that returns a yaml dump
        structured_content = tester.extract_structured_content(result, format_hint='auto')
        if structured_content:
            print("Auto-detected structured content:")
            print(f"Current temperature: {structured_content.get('currently', {}).get('current_temperature')}")
            print(f"Weather description: {structured_content.get('currently', {}).get('description')}")

            # Print forecast
            forecasts = structured_content.get('currently', {}).get('forecasts', [])
            if forecasts:
                print("Forecast for the next few days:")
                for forecast in forecasts:
                    print(
                        f"  {forecast.get('date')}: High {forecast.get('high_temperature')}°, Low {forecast.get('low_temperature')}°")

        # Explicitly try JSON extraction
        json_content = tester.extract_json_content(result)
        if json_content:
            print("\nExplicit JSON extraction successful")

        # Explicitly try YAML extraction (will likely be None for weather data, but shows the method)
        yaml_content = tester.extract_yaml_content(result)
        if yaml_content:
            print("\nExplicit YAML extraction successful")
        else:
            print("\nYAML extraction returned None (expected for JSON weather data)")

        # Example of handling different format hints
        formats_to_try = ['auto', 'json', 'yaml']
        for format_hint in formats_to_try:
            parsed_content = tester.extract_structured_content(result, format_hint=format_hint)
            if parsed_content:
                print(f"\nSuccessfully parsed with format_hint='{format_hint}'")
            else:
                print(f"\nFailed to parse with format_hint='{format_hint}'")



if __name__ == "__main__":
    asyncio.run(run_example())