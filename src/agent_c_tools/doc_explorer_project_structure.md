# Doc Explorer Project Structure

This is a greenfield project that will be implemented as a completely separate package from agent_c_tools, with its own repository and structure.

## Repository Layout

```
doc_explorer/
├── src/
│   ├── doc_explorer/
│   │   ├── __init__.py
│   │   ├── tool.py                 # Main tool implementation
│   │   ├── html_parser.py          # HTML parsing utilities
│   │   ├── selector_engine.py      # CSS/XPath selector implementation
│   │   ├── html_renderer.py        # HTML to markdown/output formatting
│   │   ├── html_modifier.py        # Document modification utilities
│   │   └── errors.py               # Custom error definitions
│   ├── pyproject.toml
│   └── setup.py
├── tests/
│   ├── test_parser.py
│   ├── test_selectors.py
│   ├── test_renderer.py
│   ├── test_modifier.py
│   └── sample_data/                # HTML test files
└── README.md
```

## Core Python Files

1. `__init__.py` - Package exports
2. `errors.py` - Custom exception classes
3. `html_parser.py` - HTML document parsing and structure analysis
4. `selector_engine.py` - CSS and XPath selector implementation
5. `html_renderer.py` - HTML to Markdown conversion and rendering
6. `html_modifier.py` - HTML modification utilities
7. `tool.py` - Main toolset implementation

## Dependencies

- **Beautiful Soup 4**: HTML parsing and manipulation
- **lxml**: Backend for BeautifulSoup and XPath support
- **html2text**: HTML to Markdown conversion
- **cssselect**: CSS selector to XPath translation

## Installation Process

After creating the repository structure and implementing the code:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
cd doc_explorer
pip install -e .
```

## Usage with Agent C

To use this tool with Agent C, it will need to be installed in the Agent C environment and then activated in the tool chest.