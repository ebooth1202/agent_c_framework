import asyncio
import logging
from debug_tool import ToolDebugger


async def run_example():
    """Simple example of how to use the ToolDebugger"""
    # Create the tool tester
    tester = ToolDebugger(log_level=logging.INFO, init_local_workspaces=False)

    # Setup a weather tool as a simple example
    # tool_opts is how you pass in required keys to, without loading .env
    # tool_opts={'FLASHDOCS_API_KEY': api_key}
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

    # Get structured content (parsed JSON)
    structured_content = tester.extract_structured_content(result)
    if structured_content:
        print("Current temperature:", structured_content.get('currently', {}).get('current_temperature'))
        print("Weather description:", structured_content.get('currently', {}).get('description'))

        # Print forecast
        forecasts = structured_content.get('currently', {}).get('forecasts', [])
        if forecasts:
            print("Forecast for the next few days:")
            for forecast in forecasts:
                print(
                    f"  {forecast.get('date')}: High {forecast.get('high_temperature')}°, Low {forecast.get('low_temperature')}°")




if __name__ == "__main__":
    asyncio.run(run_example())