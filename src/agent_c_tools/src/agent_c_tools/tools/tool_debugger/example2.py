import asyncio
import logging
from debug_tool import ToolDebugger


async def run_example():
    """Simple example of how to use the ToolDebugger"""
    # Create the tool tester
    tester = ToolDebugger(log_level=logging.INFO)

    # Setup a weather tool as a simple example
    # tool_opts is how you pass in required keys to, without loading .env
    # tool_opts={'FLASHDOCS_API_KEY': api_key}
    await tester.setup_tool(tool_import_path='agent_c_tools.MarkdownToHtmlReportTools',
                            tool_opts={})

    # Get tool info
    tester.print_tool_info()

    # Get the correct tool names
    tool_names = tester.get_available_tool_names()
    print(f"\nAvailable tool names: {tool_names}")

    # Initialize workspace if needed


    # Run a tool call, pass in parameters.  Format of the tool name is <toolset_name>_<function_name>
    result = await tester.run_tool_test(
        tool_name='generate_md_viewer',
        tool_params={"workspace": "robots",
                     "file_path": "requirements",
                     "output_filename": "test_viewer.html",
                     "title": "Markdown Viewer Smoke‑Test", }
    )

    # Get raw content (JSON string)
    content = tester.extract_content_from_results(result)
    if content:
        print("Raw content:", content)

    # Get structured content (parsed JSON)
    structured_content = tester.extract_structured_content(result)

if __name__ == "__main__":
    asyncio.run(run_example())
