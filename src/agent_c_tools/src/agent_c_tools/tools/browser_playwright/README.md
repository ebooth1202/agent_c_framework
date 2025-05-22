# Browser Playwright Tool

## Overview
The Browser Playwright tool provides web browser automation capabilities for Agent C using the Playwright framework. This tool allows agents to navigate websites, interact with elements, capture screenshots, and more without requiring visual processing.

## Features
- Browser session management (initialization, navigation, and cleanup)
- Page interaction (clicking, typing, selecting options)
- Form filling
- Tab management
- Screenshot capture
- Accessibility snapshots

## Requirements
- Python 3.8+
- Playwright package: `pip install playwright`
- Browser binaries: `playwright install` (to install Chromium, Firefox, and WebKit)

## Usage

### Initializing a Browser
```python
result = await browser.initialize_browser(
    browser_type="chromium",  # Options: chromium, firefox, webkit
    headless=False,           # Set to True for headless mode
    viewport_width=1280,
    viewport_height=720
)
```

### Navigating to a URL
```python
result = await browser.navigate(
    url="https://example.com",
    wait_until="load"  # Options: load, domcontentloaded, networkidle, commit
)
```

### Getting a Page Snapshot
```python
result = await browser.get_snapshot()
# Access elements with their references from the snapshot
```

### Interacting with Elements
```python
# Click an element
result = await browser.click(element_ref="0/1/2")

# Type text into an input
result = await browser.type_text(
    element_ref="0/3/0", 
    text="Hello, world!",
    clear_first=True
)
```

### Taking Screenshots
```python
result = await browser.take_screenshot(
    full_page=True,
    file_format="png"  # Options: png, jpeg
)
```

### Managing Tabs
```python
# Create a new tab
result = await browser.manage_tabs(
    action="new", 
    url="https://example.org"
)

# List all tabs
result = await browser.manage_tabs(action="list")

# Select a tab
result = await browser.manage_tabs(
    action="select", 
    tab_index=1
)

# Close a tab
result = await browser.manage_tabs(
    action="close", 
    tab_index=2
)
```

### Closing the Browser
```python
result = await browser.close_browser()
```

## Element References
Element references are obtained from page snapshots and are used to target specific elements for interaction. These references are structured strings that uniquely identify elements in the page's accessibility tree.