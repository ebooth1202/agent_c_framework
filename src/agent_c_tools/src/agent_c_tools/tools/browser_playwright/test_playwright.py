import asyncio
from agent_c_tools.tools.browser_playwright.tool import BrowserPlaywrightTools

async def test_browser_playwright():
    # Initialize the tool
    browser_tool = BrowserPlaywrightTools()
    
    # Initialize a browser session
    init_result = await browser_tool.initialize_browser(
        browser_type="chromium",
        headless=False
    )
    print(f"Initialization result: {init_result}")
    
    if not init_result.get("success", False):
        print("Failed to initialize browser")
        return
    
    # Navigate to a URL
    nav_result = await browser_tool.navigate(url="https://example.com")
    print(f"Navigation result: {nav_result}")
    
    # Get a snapshot of the page
    snapshot_result = await browser_tool.get_snapshot()
    print(f"Snapshot result available: {snapshot_result.get('success', False)}")
    
    # Take a screenshot
    screenshot_result = await browser_tool.take_screenshot(full_page=True)
    print(f"Screenshot result: {screenshot_result}")
    
    # Create a new tab
    tab_result = await browser_tool.manage_tabs(action="new", url="https://opensource.org")
    print(f"New tab result: {tab_result}")
    
    # List all tabs
    tabs_result = await browser_tool.manage_tabs(action="list")
    print(f"Tabs list result: {tabs_result}")
    
    # Wait a bit to see the results
    await asyncio.sleep(3)
    
    # Close the browser
    close_result = await browser_tool.close_browser()
    print(f"Close result: {close_result}")


if __name__ == "__main__":
    asyncio.run(test_browser_playwright())