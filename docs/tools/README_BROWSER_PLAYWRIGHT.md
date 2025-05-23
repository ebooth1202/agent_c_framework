# Browser Playwright Tool

## What This Tool Does

The Browser Playwright Tool provides powerful web browser automation capabilities for agents, enabling them to navigate websites, interact with web elements, capture screenshots, and extract information from web pages. Built on the robust Playwright framework, this tool allows agents to perform complex web interactions without requiring visual processing, instead using structured accessibility information to understand and interact with web content.

## Key Capabilities

Agents equipped with this tool can perform sophisticated web automation tasks:

- **Browser Management**: Initialize and control multiple browser types (Chromium, Firefox, WebKit)
- **Navigation**: Visit URLs, handle page loading, and manage browser history
- **Element Interaction**: Click buttons, fill forms, select options, and interact with any web element
- **Tab Management**: Create, switch between, and manage multiple browser tabs
- **Screenshot Capture**: Take full-page or element-specific screenshots
- **Page Analysis**: Extract structured accessibility information from web pages
- **Form Automation**: Fill out complex forms and submit data
- **Content Extraction**: Retrieve text, links, and other content from web pages

## Practical Use Cases

### Web Research and Data Collection
- **Automated Research**: Navigate through multiple websites to gather information
- **Data Extraction**: Extract structured data from web pages and tables
- **Content Monitoring**: Check websites for changes or updates
- **Competitive Analysis**: Gather information from competitor websites

### Web Application Testing
- **User Journey Testing**: Simulate user interactions through web applications
- **Form Testing**: Validate form functionality and data submission
- **Cross-Browser Testing**: Test web applications across different browser engines
- **Accessibility Testing**: Verify web accessibility using structured page analysis

### Content Creation and Documentation
- **Screenshot Documentation**: Capture visual documentation of web interfaces
- **Tutorial Creation**: Document step-by-step web processes with screenshots
- **Bug Reporting**: Capture evidence of web application issues
- **Process Documentation**: Document web-based workflows and procedures

### Automation and Integration
- **Web Scraping**: Extract data from websites for analysis or integration
- **Form Automation**: Automate repetitive form filling tasks
- **Web API Testing**: Test web interfaces and user interactions
- **Content Publishing**: Automate content publication to web platforms

## Configuration Requirements

### Installation Prerequisites

The Browser Playwright Tool requires specific software to be installed:

```bash
# Install the Playwright Python package
pip install playwright

# Install browser binaries (required for browser automation)
playwright install

# Optional: Install specific browsers only
playwright install chromium firefox webkit
```

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 2GB RAM for browser operations
- **Disk Space**: ~300MB for browser binaries

### Environment Configuration

No additional environment variables are required for basic operation. The tool automatically manages browser sessions and resources.

## Example Interactions

### Basic Web Navigation and Screenshot

**User**: "Please visit the Python.org website and take a screenshot of the homepage."

**Agent**: *Initializes a browser, navigates to python.org, captures a full-page screenshot, and provides the image for review.*

```python
# Agent performs these operations:
# 1. Initialize browser session
await browser.initialize_browser(browser_type="chromium", headless=False)

# 2. Navigate to the website
await browser.navigate(url="https://python.org")

# 3. Take a screenshot
await browser.take_screenshot(full_page=True, file_format="png")
```

### Form Filling and Interaction

**User**: "Go to the contact form on example.com and fill it out with my information."

**Agent**: *Navigates to the contact page, analyzes the form structure using accessibility snapshots, fills in the required fields, and submits the form.*

```python
# Agent workflow:
# 1. Navigate to the contact page
await browser.navigate(url="https://example.com/contact")

# 2. Get page structure
snapshot = await browser.get_snapshot()

# 3. Fill form fields (using element references from snapshot)
await browser.type_text(element_ref="0/2/1", text="John Doe")
await browser.type_text(element_ref="0/2/3", text="john@example.com")
await browser.type_text(element_ref="0/2/5", text="Hello, this is a test message.")

# 4. Submit the form
await browser.click(element_ref="0/2/7")  # Submit button
```

### Multi-Tab Research

**User**: "Research the top 3 Python web frameworks by opening their official websites in separate tabs and taking screenshots of each."

**Agent**: *Opens multiple tabs for Django, Flask, and FastAPI websites, captures screenshots from each tab, and provides a comparison of the frameworks' homepages.*

```python
# Agent performs:
# 1. Create tabs for each framework
await browser.manage_tabs(action="new", url="https://djangoproject.com")
await browser.manage_tabs(action="new", url="https://flask.palletsprojects.com")
await browser.manage_tabs(action="new", url="https://fastapi.tiangolo.com")

# 2. Switch to each tab and capture screenshots
for tab_index in range(3):
    await browser.manage_tabs(action="select", tab_index=tab_index)
    await browser.take_screenshot(full_page=True)
```

### Web Application Testing

**User**: "Test the login functionality on our staging website and verify the dashboard loads correctly."

**Agent**: *Navigates to the login page, fills in test credentials, submits the form, verifies successful login by checking for dashboard elements, and captures evidence screenshots.*

## API Reference

### Browser Session Management

#### `initialize_browser`
Initializes a new browser session with specified configuration.

**Parameters:**
- `browser_type` (required): Browser engine to use
  - Options: `"chromium"`, `"firefox"`, `"webkit"`
- `headless` (optional): Run browser without GUI (default: `false`)
- `user_agent` (optional): Custom user agent string
- `viewport_width` (optional): Browser window width in pixels (default: 1280)
- `viewport_height` (optional): Browser window height in pixels (default: 720)

**Returns:** Session information including session ID and initialization status.

#### `close_browser`
Closes the browser session and cleans up resources.

**Parameters:**
- `session_id` (optional): Specific session to close (uses current session if not specified)

**Returns:** Confirmation of browser closure and resource cleanup.

### Navigation

#### `navigate`
Navigates to a specified URL in the current browser session.

**Parameters:**
- `url` (required): Target URL to navigate to
- `session_id` (optional): Browser session to use
- `wait_until` (optional): Navigation completion criteria
  - Options: `"load"`, `"domcontentloaded"`, `"networkidle"`, `"commit"`
  - Default: `"load"`

**Returns:** Navigation result including page title and final URL.

### Page Analysis

#### `get_snapshot`
Captures a structured accessibility snapshot of the current page.

**Parameters:**
- `session_id` (optional): Browser session to use
- `include_hidden` (optional): Include hidden elements in snapshot (default: `false`)

**Returns:** Structured representation of page elements with accessibility information and element references for interaction.

### Element Interaction

#### `click`
Clicks on a specified element in the page.

**Parameters:**
- `element_ref` (required): Element reference from page snapshot
- `session_id` (optional): Browser session to use
- `force` (optional): Force click even if element is not visible (default: `false`)
- `modifiers` (optional): Keyboard modifiers to hold during click
  - Options: `["Alt"]`, `["Control"]`, `["Meta"]`, `["Shift"]`

**Returns:** Result of the click operation including any page changes.

#### `type_text`
Types text into an input element.

**Parameters:**
- `element_ref` (required): Element reference from page snapshot
- `text` (required): Text to type into the element
- `session_id` (optional): Browser session to use
- `delay` (optional): Delay between keystrokes in milliseconds (default: 0)
- `clear_first` (optional): Clear existing text before typing (default: `true`)

**Returns:** Result of the text input operation.

### Screenshot Capture

#### `take_screenshot`
Captures a screenshot of the current page or specific element.

**Parameters:**
- `session_id` (optional): Browser session to use
- `element_ref` (optional): Element reference to screenshot (full page if not specified)
- `full_page` (optional): Capture entire page including scrolled content (default: `false`)
- `quality` (optional): JPEG quality from 0-100 (default: 80)
- `file_format` (optional): Image format
  - Options: `"png"`, `"jpeg"`
  - Default: `"png"`

**Returns:** Screenshot data and file information.

### Tab Management

#### `manage_tabs`
Manages browser tabs: create, close, select, or list tabs.

**Parameters:**
- `action` (required): Tab management action
  - Options: `"new"`, `"close"`, `"select"`, `"list"`
- `session_id` (optional): Browser session to use
- `url` (optional): URL for new tab creation
- `tab_index` (optional): Tab index for select/close operations

**Returns:** Result of tab operation including updated tab information.

## Best Practices

### Element Interaction Workflow
1. **Always get a page snapshot first** before attempting to interact with elements
2. **Use element references** from snapshots for reliable element targeting
3. **Wait for page loads** using appropriate `wait_until` parameters
4. **Handle dynamic content** by taking fresh snapshots after page changes

### Resource Management
- **Close browser sessions** when automation tasks are complete
- **Use headless mode** for background operations to improve performance
- **Manage multiple tabs** efficiently to avoid resource exhaustion

### Error Handling
- **Check return values** for success/failure status
- **Handle navigation timeouts** gracefully
- **Verify element existence** in snapshots before interaction
- **Use appropriate wait strategies** for dynamic content

### Performance Optimization
- **Reuse browser sessions** for multiple operations when possible
- **Use appropriate viewport sizes** to match target user experience
- **Consider headless mode** for non-visual automation tasks
- **Clean up resources** promptly to prevent memory leaks

## Troubleshooting

### Common Issues

#### Browser Installation Problems
**Problem**: "Failed to initialize Playwright" error
**Solution**: Ensure browser binaries are installed:
```bash
playwright install
```

#### Element Not Found
**Problem**: Cannot interact with elements on the page
**Solution**: 
1. Take a fresh page snapshot after navigation
2. Verify element references from the snapshot
3. Ensure page has fully loaded before interaction

#### Navigation Timeouts
**Problem**: Page navigation hangs or times out
**Solution**:
1. Use appropriate `wait_until` parameter for the page type
2. Check network connectivity and page availability
3. Consider using `"domcontentloaded"` for faster loading

#### Screenshot Issues
**Problem**: Screenshots are blank or incomplete
**Solution**:
1. Ensure page has fully loaded before capturing
2. Use `full_page=true` for complete page capture
3. Verify browser session is active and page is visible

### Performance Issues

#### High Memory Usage
- Close unused browser sessions promptly
- Avoid keeping multiple browser instances open simultaneously
- Use headless mode when visual interface is not needed

#### Slow Operations
- Use appropriate wait strategies instead of fixed delays
- Optimize viewport sizes for your use case
- Consider using faster browser engines (Chromium is typically fastest)

### Browser-Specific Considerations

#### Chromium
- Best performance and compatibility
- Recommended for most automation tasks
- Full support for modern web standards

#### Firefox
- Good for testing cross-browser compatibility
- May have different behavior with some web applications
- Slightly slower than Chromium for automation

#### WebKit
- Essential for testing Safari-like behavior
- May have limitations with some modern web features
- Useful for mobile web testing scenarios

## Security Considerations

- **Sensitive Data**: Be cautious when automating forms with sensitive information
- **Authentication**: Handle login credentials securely and avoid hardcoding
- **Network Security**: Be aware of the websites and data being accessed
- **Resource Limits**: Implement appropriate timeouts and resource limits for automation tasks

This tool provides powerful web automation capabilities while maintaining security and reliability through structured interaction patterns and comprehensive error handling.