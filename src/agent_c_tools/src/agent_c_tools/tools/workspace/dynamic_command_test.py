import asyncio
import logging
from agent_c_tools.tools.tool_debugger.debug_tool import ToolDebugger


async def run_example():
    """Simple example of how to use the ToolDebugger"""
    # Create the tool tester
    tester = ToolDebugger(log_level=logging.INFO)

    # Setup a weather tool as a simple example
    # tool_opts is how you pass in required keys to, without loading .env
    # tool_opts={'FLASHDOCS_API_KEY': api_key}
    # from agent_c_tools.tools.workspace
    await tester.setup_tool(tool_import_path='agent_c_tools.tools.workspace.DynamicCommandTools',
                            tool_opts={})

    # Get tool info
    # tester.print_tool_info()

    # Get the correct tool names
    # tool_names = tester.get_available_tool_names()
    # print(f"\nAvailable tool names: {tool_names}")

    # Initialize workspace if needed


    # Run a tool call, pass in parameters.  Format of the tool name is <toolset_name>_<function_name>

    # Test npm functionality
    print("\n=== Testing npm functionality ===")
    result_npm = await tester.run_tool_test(
        tool_name='run_npm',
        tool_params={"path": "//deep_code",
                     "args": "--version",}
    )
    
    # Test pnpm functionality 
    print("\n=== Testing pnpm functionality ===")
    result_pnpm = await tester.run_tool_test(
        tool_name='run_pnpm',
        tool_params={"path": "//deep_code",
                     "args": "--version",
                     "suppress_success_output": True}
    )
    
    # Test both results
    results = {'npm': result_npm, 'pnpm': result_pnpm}
    
    for tool_name, result in results.items():
        print(f"\n=== {tool_name.upper()} Results ===")
        if "is not on a valid toolset" in str(result):
            print(f"Error: {tool_name} tool name is not valid")
            continue
            
        content = tester.extract_content_from_results(result)
        if content:
            print(f"{tool_name} output:\n{content}")
        else:
            print(f"No content extracted for {tool_name}")
    
    # Return the last result for backward compatibility
    result = result_pnpm
    
    # Print available tool names at the end for reference
    print("\n=== Available tool names ===")
    tool_names = tester.get_available_tool_names()
    print([name for name in tool_names if 'run_' in name])  # Filter to show just the run_ tools

if __name__ == "__main__":
    asyncio.run(run_example())
