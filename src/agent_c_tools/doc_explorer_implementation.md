# Doc Explorer Implementation Plan

## Package Structure

The complete source package structure will be as follows:

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

## Core Classes Implementation

### 1. `__init__.py`

```python
from doc_explorer.tool import DocExplorerTools

__all__ = ['DocExplorerTools']
```

### 2. `errors.py`

```python
class DocExplorerError(Exception):
    """Base exception for Doc Explorer errors"""
    pass


class ParserError(DocExplorerError):
    """Error during HTML parsing"""
    pass


class SelectorError(DocExplorerError):
    """Error in CSS selector or XPath expression"""
    pass


class ModificationError(DocExplorerError):
    """Error during HTML modification"""
    pass


class RenderError(DocExplorerError):
    """Error during rendering preparation"""
    pass
```

### 3. `html_parser.py`

```python
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup, Tag
from collections import Counter

from .errors import ParserError


class HTMLParser:
    """HTML parsing utilities for Doc Explorer"""

    def __init__(self, workspace):
        """Initialize with workspace for file access"""
        self.workspace = workspace
        self.logger = logging.getLogger(__name__)

    async def load_document(self, file_path: str) -> BeautifulSoup:
        """Load HTML document from workspace path

        Args:
            file_path: Path to HTML file relative to workspace root

        Returns:
            BeautifulSoup object with parsed HTML

        Raises:
            ParserError: If file cannot be read or parsed
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                raise ParserError(f'Invalid file path: {file_path}')

            # Read the file content
            with open(full_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Parse HTML with BeautifulSoup using lxml parser
            soup = BeautifulSoup(html_content, 'lxml')
            return soup

        except Exception as e:
            error_msg = f'Error loading HTML document: {str(e)}'
            self.logger.error(error_msg)
            raise ParserError(error_msg) from e

    async def get_structure(self, soup: BeautifulSoup, max_depth: int = 5, 
                           sample_count: int = 3) -> Dict[str, Any]:
        """Generate a structure summary of the HTML document

        Args:
            soup: BeautifulSoup object with parsed HTML
            max_depth: Maximum depth to explore in the document structure
            sample_count: Number of sample elements to include at each level

        Returns:
            Dictionary with structure information
        """
        try:
            structure = {
                'title': self._get_title(soup),
                'meta': self._extract_meta_info(soup),
                'structure': self._analyze_structure(soup, max_depth, sample_count)
            }
            return structure
        except Exception as e:
            error_msg = f'Error analyzing document structure: {str(e)}'
            self.logger.error(error_msg)
            raise ParserError(error_msg) from e

    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract the document title"""
        title_tag = soup.title
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        return "[No title]"  

    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags information"""
        meta_info = {}
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                meta_info[meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                meta_info[meta['property']] = meta.get('content', '')
        return meta_info

    def _analyze_structure(self, soup: BeautifulSoup, max_depth: int, 
                          sample_count: int) -> Dict[str, Any]:
        """Analyze document structure recursively"""
        root_children = soup.find('html')
        if not root_children:
            root_children = soup  # Handle fragments without html tag

        return self._analyze_element(root_children, 0, max_depth, sample_count, {})

    def _analyze_element(self, element: Tag, current_depth: int, max_depth: int, 
                        sample_count: int, path_counts: Dict[str, int]) -> Dict[str, Any]:
        """Recursively analyze an element and its children"""
        if current_depth > max_depth:
            return {
                'tag': element.name,
                'truncated': True,
                'children_count': len(element.find_all(recursive=False))
            }

        # Count children by tag type
        child_elements = element.find_all(recursive=False)
        child_tags = [child.name for child in child_elements if hasattr(child, 'name')]
        tag_counts = dict(Counter(child_tags))

        # Record path for id and class counts
        for child in child_elements:
            if not hasattr(child, 'name'):
                continue  # Skip NavigableString

            # Track paths with IDs
            if child.get('id'):
                path = f"#{child['id']}"
                path_counts[path] = path_counts.get(path, 0) + 1

            # Track paths with classes
            if child.get('class'):
                for cls in child.get('class'):
                    path = f".{cls}"
                    path_counts[path] = path_counts.get(path, 0) + 1

        # Get sample attributes from children
        sample_elements = []
        for i, child in enumerate(child_elements):
            if i >= sample_count:
                break
            if hasattr(child, 'name'):
                attrs = dict(child.attrs) if hasattr(child, 'attrs') else {}
                sample = {
                    'tag': child.name,
                    'attributes': attrs
                }
                
                # Add text snippet if it exists and isn't just whitespace
                if child.string and child.string.strip():
                    # Truncate long text
                    text = child.string.strip()
                    if len(text) > 100:
                        text = text[:100] + "..."
                    sample['text'] = text
                
                sample_elements.append(sample)

        # Recursively analyze children
        child_structures = []
        for child in child_elements:
            if hasattr(child, 'name') and len(child_structures) < sample_count:
                child_structure = self._analyze_element(
                    child, current_depth + 1, max_depth, sample_count, path_counts
                )
                child_structures.append(child_structure)

        # Build result
        result = {
            'tag': element.name,
            'attributes': dict(element.attrs) if hasattr(element, 'attrs') else {},
            'children_count': len(child_elements),
            'children_by_tag': tag_counts
        }

        if child_structures:
            result['sample_children'] = child_structures

        if sample_elements:
            result['sample_elements'] = sample_elements

        return result
```

### 4. `selector_engine.py`

```python
import logging
from typing import List, Optional, Union, Dict, Any
from bs4 import BeautifulSoup, Tag
import re
import cssselect
import lxml.etree
from lxml.cssselect import CSSSelector

from .errors import SelectorError


class SelectorEngine:
    """Engine for CSS selectors and XPath expressions"""

    def __init__(self, soup: BeautifulSoup):
        """Initialize with BeautifulSoup object"""
        self.soup = soup
        self.lxml_doc = None  # For XPath operations
        self.logger = logging.getLogger(__name__)

    def query(self, selector: str, selector_type: str = "css", limit: int = None) -> List[Tag]:
        """Find elements using either CSS selector or XPath

        Args:
            selector: CSS selector or XPath expression
            selector_type: "css" or "xpath"
            limit: Maximum number of results to return

        Returns:
            List of matching BeautifulSoup Tag objects

        Raises:
            SelectorError: If selector is invalid or no elements match
        """
        try:
            if selector_type.lower() == "css":
                elements = self.soup.select(selector)
            elif selector_type.lower() == "xpath":
                # For XPath, convert to lxml document if needed
                if self.lxml_doc is None:
                    self.lxml_doc = lxml.etree.fromstring(
                        str(self.soup), lxml.etree.HTMLParser()
                    )
                elements = []
                for element in self.lxml_doc.xpath(selector):
                    # Convert lxml elements to BeautifulSoup elements by finding them in the soup
                    if hasattr(element, 'xpath'):
                        # Get a unique path to this element
                        path = self.lxml_doc.getpath(element)
                        # Find the equivalent in BeautifulSoup using the path
                        bs_element = self.soup.select_one(self._xpath_to_css(path))
                        if bs_element:
                            elements.append(bs_element)
            else:
                raise SelectorError(f"Unsupported selector type: {selector_type}")

            if limit is not None:
                elements = elements[:limit]

            return elements

        except Exception as e:
            error_msg = f'Error executing {selector_type} selector "{selector}": {str(e)}'
            self.logger.error(error_msg)
            raise SelectorError(error_msg) from e

    def get_element_info(self, element: Tag) -> Dict[str, Any]:
        """Get detailed information about an element

        Args:
            element: BeautifulSoup Tag object

        Returns:
            Dictionary with element information
        """
        try:
            info = {
                'tag': element.name,
                'attributes': dict(element.attrs) if hasattr(element, 'attrs') else {}
            }

            # Get selector paths to element
            info['path'] = {
                'css': self.get_css_path(element),
                'xpath': self.get_xpath(element)
            }

            # Add text content if it exists
            text = element.get_text(strip=True)
            if text:
                # Truncate long text
                if len(text) > 200:
                    text = text[:200] + "..."
                info['text'] = text

            # Add direct children info
            children = element.find_all(recursive=False)
            if children:
                info['children_count'] = len(children)
                info['children_tags'] = [child.name for child in children if hasattr(child, 'name')]

            return info

        except Exception as e:
            error_msg = f'Error extracting element info: {str(e)}'
            self.logger.error(error_msg)
            raise SelectorError(error_msg) from e

    def get_css_path(self, element: Tag) -> str:
        """Get a CSS selector path to the element"""
        if not element or not element.name:
            return ""

        components = []
        current = element

        while current and current.name != '[document]':
            # Start with tag name
            selector = current.name

            # Add ID if it exists (most specific)
            if current.get('id'):
                selector = f"{selector}#{current['id']}"
                components.insert(0, selector)
                break  # ID is unique, no need to go further up the tree

            # Add classes
            if current.get('class'):
                classes = '.'.join(current['class'])
                selector = f"{selector}.{classes}"

            # Add :nth-child for more specificity if no ID
            if current.parent:
                siblings = [sibling for sibling in current.parent.children 
                          if sibling.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    selector = f"{selector}:nth-child({index})"

            components.insert(0, selector)
            current = current.parent

        return " > ".join(components)

    def get_xpath(self, element: Tag) -> str:
        """Get an XPath to the element"""
        if not element:
            return ""

        components = []
        current = element

        while current and current.name != '[document]':
            # Start with tag name
            path_part = current.name

            # Add ID if it exists
            if current.get('id'):
                path_part = f"{path_part}[@id='{current['id']}']"
                components.insert(0, path_part)
                break  # ID is unique, no need to go further

            # Add position among siblings with same tag
            if current.parent:
                siblings = [sibling for sibling in current.parent.children 
                           if sibling.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    path_part = f"{path_part}[{index}]"

            components.insert(0, path_part)
            current = current.parent

        return "/" + "/".join(components)

    def _xpath_to_css(self, xpath: str) -> str:
        """Convert simple XPath expressions to CSS selectors for BeautifulSoup
        This handles basic cases only - not a complete conversion"""
        # Handle direct child paths without predicates
        path = xpath.replace('//', ' ')
        path = path.replace('/', ' > ')
        
        # Handle ID predicates
        path = re.sub(r'\[@id=["\']([^"\']*)["\']]', r'#\1', path)
        
        # Remove position predicates - BeautifulSoup doesn't need them for structure
        path = re.sub(r'\[\d+]', '', path)
        
        return path
```

### 5. `html_renderer.py`

```python
import logging
import json
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup, Tag
import html2text

from .errors import RenderError


class HTMLRenderer:
    """Handles HTML rendering and format conversion"""

    def __init__(self):
        """Initialize with default settings"""
        self.logger = logging.getLogger(__name__)
        self.html2text_converter = html2text.HTML2Text()
        self.html2text_converter.ignore_links = False
        self.html2text_converter.ignore_images = False
        self.html2text_converter.body_width = 0  # No wrapping

    def to_markdown(self, html_content: str) -> str:
        """Convert HTML to Markdown

        Args:
            html_content: HTML content to convert

        Returns:
            Markdown representation of the HTML content
        """
        try:
            return self.html2text_converter.handle(html_content)
        except Exception as e:
            error_msg = f'Error converting HTML to Markdown: {str(e)}'
            self.logger.error(error_msg)
            raise RenderError(error_msg) from e

    def prepare_render_data(self, html_content: str, 
                          title: str = "HTML Preview",
                          highlight_selector: Optional[str] = None) -> Dict[str, Any]:
        """Prepare data for RenderMedia event

        Args:
            html_content: HTML content to render
            title: Title for the rendered content
            highlight_selector: Optional CSS selector for elements to highlight

        Returns:
            Dictionary with render media data
        """
        try:
            # Create a base structure for the rendered HTML
            render_data = {
                "title": title,
                "mime": "text/html",
            }

            # If highlighting is requested, add it with CSS
            if highlight_selector:
                # Parse the HTML
                soup = BeautifulSoup(html_content, "lxml")
                
                # Add a style tag with highlighting CSS
                style = soup.new_tag("style")
                highlight_css = f"""{highlight_selector} {{
                    background-color: #ffff00 !important;
                    outline: 2px solid #ff9900 !important;
                }}"""
                style.string = highlight_css
                
                # Add style to head or create head if it doesn't exist
                if soup.head:
                    soup.head.append(style)
                else:
                    head = soup.new_tag("head")
                    head.append(style)
                    if soup.html:
                        soup.html.insert(0, head)
                    else:
                        # Create basic structure if needed
                        html = soup.new_tag("html")
                        html.append(head)
                        # Move all content to the body
                        body = soup.new_tag("body")
                        for content in list(soup.contents):
                            if content.name not in ["html", "head"]:
                                body.append(content)
                        html.append(body)
                        soup = BeautifulSoup(str(html), "lxml")
                
                html_content = str(soup)

            render_data["data"] = html_content
            return render_data

        except Exception as e:
            error_msg = f'Error preparing render data: {str(e)}'
            self.logger.error(error_msg)
            raise RenderError(error_msg) from e
```

### 6. `html_modifier.py`

```python
import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from bs4 import BeautifulSoup, Tag

from .errors import ModificationError
from .selector_engine import SelectorEngine


class HTMLModifier:
    """Handles HTML document modifications"""

    def __init__(self, soup: BeautifulSoup):
        """Initialize with BeautifulSoup object"""
        self.soup = soup
        self.selector_engine = SelectorEngine(soup)
        self.logger = logging.getLogger(__name__)

    def replace_element_content(self, selector: str, new_content: str, 
                              selector_type: str = "css") -> Tuple[BeautifulSoup, int]:
        """Replace content of elements matching selector

        Args:
            selector: CSS selector or XPath identifying elements to modify
            new_content: New HTML content to replace the matched elements with
            selector_type: Type of selector: 'css' or 'xpath'

        Returns:
            Tuple of (modified soup object, number of elements modified)

        Raises:
            ModificationError: If modification fails
        """
        try:
            # Find elements to replace
            elements = self.selector_engine.query(selector, selector_type)
            if not elements:
                raise ModificationError(f"No elements found matching {selector_type} selector: {selector}")

            # Parse new content
            new_elements = BeautifulSoup(new_content, "lxml").body
            if not new_elements:
                raise ModificationError("Invalid new content: could not parse HTML")

            # Extract the contents from the body tag
            new_contents = list(new_elements.children)

            # Replace each element
            for element in elements:
                # Clear existing content
                element.clear()
                
                # Add new content
                for content in new_contents:
                    # We need to create a copy of each content item
                    # to avoid issues with inserting the same item multiple times
                    element.append(content.copy() if hasattr(content, 'copy') else content)

            return self.soup, len(elements)

        except Exception as e:
            if isinstance(e, ModificationError):
                raise
            error_msg = f'Error replacing element content: {str(e)}'
            self.logger.error(error_msg)
            raise ModificationError(error_msg) from e

    def modify_attributes(self, selector: str, attributes: Dict[str, Optional[str]], 
                         selector_type: str = "css") -> Tuple[BeautifulSoup, int]:
        """Add or modify attributes for elements matching selector

        Args:
            selector: CSS selector or XPath identifying elements to modify
            attributes: Dictionary of attributes to set (None value removes attribute)
            selector_type: Type of selector: 'css' or 'xpath'

        Returns:
            Tuple of (modified soup object, number of elements modified)

        Raises:
            ModificationError: If modification fails
        """
        try:
            # Find elements to modify
            elements = self.selector_engine.query(selector, selector_type)
            if not elements:
                raise ModificationError(f"No elements found matching {selector_type} selector: {selector}")

            # Modify attributes for each element
            for element in elements:
                for attr_name, attr_value in attributes.items():
                    if attr_value is None:
                        # Remove attribute if None
                        if attr_name in element.attrs:
                            del element.attrs[attr_name]
                    else:
                        # Set attribute
                        element.attrs[attr_name] = attr_value

            return self.soup, len(elements)

        except Exception as e:
            if isinstance(e, ModificationError):
                raise
            error_msg = f'Error modifying attributes: {str(e)}'
            self.logger.error(error_msg)
            raise ModificationError(error_msg) from e

    def insert_content(self, selector: str, new_content: str, 
                     position: str = "append", 
                     selector_type: str = "css") -> Tuple[BeautifulSoup, int]:
        """Insert content relative to elements matching selector

        Args:
            selector: CSS selector or XPath identifying elements
            new_content: New HTML content to insert
            position: Where to insert ("append", "prepend", "before", "after")
            selector_type: Type of selector: 'css' or 'xpath'

        Returns:
            Tuple of (modified soup object, number of elements modified)

        Raises:
            ModificationError: If modification fails
        """
        try:
            # Find elements
            elements = self.selector_engine.query(selector, selector_type)
            if not elements:
                raise ModificationError(f"No elements found matching {selector_type} selector: {selector}")

            # Parse new content
            fragment = BeautifulSoup(new_content, "lxml").body
            if not fragment:
                raise ModificationError("Invalid new content: could not parse HTML")

            # Extract the contents from the body tag
            new_contents = list(fragment.children)

            # Insert for each element
            for element in elements:
                if position == "append":
                    for content in reversed(new_contents):
                        element.append(content.copy() if hasattr(content, 'copy') else content)
                elif position == "prepend":
                    for content in reversed(new_contents):
                        element.insert(0, content.copy() if hasattr(content, 'copy') else content)
                elif position == "before":
                    for content in new_contents:
                        element.insert_before(content.copy() if hasattr(content, 'copy') else content)
                elif position == "after":
                    for content in reversed(new_contents):
                        element.insert_after(content.copy() if hasattr(content, 'copy') else content)
                else:
                    raise ModificationError(f"Invalid position: {position}")

            return self.soup, len(elements)

        except Exception as e:
            if isinstance(e, ModificationError):
                raise
            error_msg = f'Error inserting content: {str(e)}'
            self.logger.error(error_msg)
            raise ModificationError(error_msg) from e

    def remove_elements(self, selector: str, 
                      selector_type: str = "css") -> Tuple[BeautifulSoup, int]:
        """Remove elements matching selector

        Args:
            selector: CSS selector or XPath identifying elements to remove
            selector_type: Type of selector: 'css' or 'xpath'

        Returns:
            Tuple of (modified soup object, number of elements removed)

        Raises:
            ModificationError: If removal fails
        """
        try:
            # Find elements to remove
            elements = self.selector_engine.query(selector, selector_type)
            if not elements:
                raise ModificationError(f"No elements found matching {selector_type} selector: {selector}")

            # Remove each element
            for element in elements:
                element.decompose()

            return self.soup, len(elements)

        except Exception as e:
            if isinstance(e, ModificationError):
                raise
            error_msg = f'Error removing elements: {str(e)}'
            self.logger.error(error_msg)
            raise ModificationError(error_msg) from e
```

### 7. `tool.py` (Main Tool Implementation)

```python
import json
import logging
from typing import Dict, Any, Optional, List, Union, cast
from bs4 import BeautifulSoup
import asyncio

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c.models.chat_event import ChatEvent

from .html_parser import HTMLParser
from .selector_engine import SelectorEngine
from .html_renderer import HTMLRenderer
from .html_modifier import HTMLModifier
from .errors import DocExplorerError, ParserError, SelectorError, ModificationError, RenderError


class DocExplorerTools(Toolset):
    """Tools for exploring and manipulating HTML documents"""

    def __init__(self, **kwargs: Any):
        """Initialize the DocExplorer toolset

        Args:
            kwargs: Standard Toolset initialization parameters
        """
        super().__init__(name="doc_explorer", **kwargs)
        self.logger = logging.getLogger(__name__)
        self.workspace_tools = None

    async def post_init(self):
        """Post-initialization setup to access workspace tools"""
        # Access workspace tools
        if hasattr(self.tool_chest, 'active_tools') and 'workspace' in self.tool_chest.active_tools:
            self.workspace_tools = self.tool_chest.active_tools['workspace']

    def _validate_and_get_workspace_path(self, unc_path: str):
        """Validate UNC-style path and return workspace object and relative path.

        Args:
            unc_path: UNC-style path (//WORKSPACE/path)

        Returns:
            Tuple of (error_message, workspace, relative_path)
        """
        if not unc_path or not unc_path.startswith('//'):
            return f"Invalid UNC path: {unc_path}", None, None

        parts = unc_path.split('/', 3)
        if len(parts) < 4:
            return f"Invalid UNC path format: {unc_path}", None, None

        workspace_name = parts[2]
        relative_path = parts[3] if len(parts) > 3 else ''

        if not self.workspace_tools or workspace_name not in self.workspace_tools.workspaces:
            return f"Workspace not found: {workspace_name}", None, None

        workspace = self.workspace_tools.workspaces[workspace_name]
        return None, workspace, relative_path

    @json_schema(
        "Get structure information about an HTML document",
        {
            "path": {
                "type": "string",
                "description": "UNC-style path (//WORKSPACE/path) to the HTML file",
                "required": True
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum depth to explore in the document structure",
                "required": False
            },
            "sample_count": {
                "type": "integer",
                "description": "Number of sample elements to include at each level",
                "required": False
            }
        }
    )
    async def structure(self, **kwargs: Any) -> str:
        """Get structure information about an HTML document

        Args:
            path: UNC-style path (//WORKSPACE/path) to the HTML file
            max_depth: Maximum depth to explore in the structure (default: 5)
            sample_count: Number of samples to collect at each level (default: 3)

        Returns:
            JSON string with structure information or an error message
        """
        try:
            unc_path = kwargs.get("path")
            max_depth = kwargs.get("max_depth", 5)
            sample_count = kwargs.get("sample_count", 3)

            # Validate path
            error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
            if error:
                return json.dumps({"error": error})

            # Parse HTML document
            parser = HTMLParser(workspace)
            soup = await parser.load_document(relative_path)

            # Generate structure
            structure = await parser.get_structure(soup, max_depth, sample_count)

            return json.dumps({
                "success": True,
                "path": unc_path,
                "structure": structure
            })

        except DocExplorerError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            error_msg = f"Error analyzing HTML structure: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})

    @json_schema(
        "Query an HTML document using CSS selectors or XPath",
        {
            "path": {
                "type": "string",
                "description": "UNC-style path (//WORKSPACE/path) to the HTML file",
                "required": True
            },
            "selector": {
                "type": "string",
                "description": "CSS selector or XPath to query elements",
                "required": True
            },
            "selector_type": {
                "type": "string",
                "description": "Type of selector: 'css' or 'xpath'",
                "required": False
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "required": False
            }
        }
    )
    async def query(self, **kwargs: Any) -> str:
        """Query an HTML document using CSS selectors or XPath

        Args:
            path: UNC-style path (//WORKSPACE/path) to the HTML file
            selector: CSS selector or XPath to query elements
            selector_type: Type of selector: 'css' or 'xpath' (default: 'css')
            limit: Maximum number of results to return (default: 10)

        Returns:
            JSON string with query results or an error message
        """
        try:
            unc_path = kwargs.get("path")
            selector = kwargs.get("selector")
            selector_type = kwargs.get("selector_type", "css").lower()
            limit = kwargs.get("limit", 10)

            # Validate path
            error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
            if error:
                return json.dumps({"error": error})

            # Parse HTML document
            parser = HTMLParser(workspace)
            soup = await parser.load_document(relative_path)

            # Execute query
            selector_engine = SelectorEngine(soup)
            elements = selector_engine.query(selector, selector_type, limit)

            # Prepare results
            results = []
            for element in elements:
                element_info = selector_engine.get_element_info(element)
                results.append(element_info)

            return json.dumps({
                "success": True,
                "query": selector,
                "selector_type": selector_type,
                "count": len(results),
                "results": results
            })

        except DocExplorerError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            error_msg = f"Error querying HTML document: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})

    @json_schema(
        "Get the content of selected elements as Markdown",
        {
            "path": {
                "type": "string",
                "description": "UNC-style path (//WORKSPACE/path) to the HTML file",
                "required": True
            },
            "selector": {
                "type": "string",
                "description": "CSS selector or XPath to target elements for conversion",
                "required": False
            },
            "selector_type": {
                "type": "string",
                "description": "Type of selector: 'css' or 'xpath'",
                "required": False
            }
        }
    )
    async def to_markdown(self, **kwargs: Any) -> str:
        """Get the content of selected elements as Markdown

        Args:
            path: UNC-style path (//WORKSPACE/path) to the HTML file
            selector: CSS selector or XPath to target elements (if not provided, converts entire document)
            selector_type: Type of selector: 'css' or 'xpath' (default: 'css')

        Returns:
            Markdown representation of the HTML content or error message
        """
        try:
            unc_path = kwargs.get("path")
            selector = kwargs.get("selector")
            selector_type = kwargs.get("selector_type", "css").lower()

            # Validate path
            error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
            if error:
                return json.dumps({"error": error})

            # Parse HTML document
            parser = HTMLParser(workspace)
            soup = await parser.load_document(relative_path)

            # Extract requested content
            if selector:
                selector_engine = SelectorEngine(soup)
                elements = selector_engine.query(selector, selector_type)
                
                if not elements:
                    return json.dumps({
                        "error": f"No elements found matching {selector_type} selector: {selector}"
                    })
                
                # Use the first element or combine multiple elements
                if len(elements) == 1:
                    html_content = str(elements[0])
                else:
                    # Wrap multiple elements in a div for proper conversion
                    html_content = "<div>" + "".join(str(e) for e in elements) + "</div>"
            else:
                # Use the entire document
                html_content = str(soup)

            # Convert to Markdown
            renderer = HTMLRenderer()
            markdown_content = renderer.to_markdown(html_content)

            return json.dumps({
                "success": True,
                "markdown": markdown_content
            })

        except DocExplorerError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            error_msg = f"Error converting HTML to Markdown: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})

    @json_schema(
        "Modify HTML document by replacing content matching a selector",
        {
            "path": {
                "type": "string",
                "description": "UNC-style path (//WORKSPACE/path) to the HTML file",
                "required": True
            },
            "selector": {
                "type": "string",
                "description": "CSS selector or XPath identifying elements to modify",
                "required": True
            },
            "new_content": {
                "type": "string",
                "description": "New HTML content to replace the matched elements with",
                "required": True
            },
            "selector_type": {
                "type": "string",
                "description": "Type of selector: 'css' or 'xpath'",
                "required": False
            },
            "modification_type": {
                "type": "string",
                "description": "Type of modification: 'replace', 'attributes', 'insert', 'remove'",
                "required": False
            },
            "position": {
                "type": "string",
                "description": "Position for insertion: 'append', 'prepend', 'before', 'after'",
                "required": False
            },
            "attributes": {
                "type": "object",
                "description": "Attributes to set when modification_type is 'attributes'",
                "required": False
            },
            "output_path": {
                "type": "string",
                "description": "Optional path to save the modified HTML document",
                "required": False
            }
        }
    )
    async def modify(self, **kwargs: Any) -> str:
        """Modify HTML document by replacing content or attributes matching a selector

        Args:
            path: UNC-style path (//WORKSPACE/path) to the HTML file
            selector: CSS selector or XPath identifying elements to modify
            new_content: New HTML content for replacement or insertion (when applicable)
            selector_type: Type of selector: 'css' or 'xpath' (default: 'css')
            modification_type: Type of modification: 'replace', 'attributes', 'insert', 'remove' (default: 'replace')
            position: Position for insertion: 'append', 'prepend', 'before', 'after' (default: 'append')
            attributes: Dictionary of attributes to set when modification_type is 'attributes'
            output_path: Optional path to save the modified HTML document

        Returns:
            JSON string with modification status or error message
        """
        try:
            unc_path = kwargs.get("path")
            selector = kwargs.get("selector")
            new_content = kwargs.get("new_content", "")
            selector_type = kwargs.get("selector_type", "css").lower()
            modification_type = kwargs.get("modification_type", "replace").lower()
            position = kwargs.get("position", "append").lower()
            attributes = kwargs.get("attributes", {})
            output_path = kwargs.get("output_path")

            # Validate path
            error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
            if error:
                return json.dumps({"error": error})

            # Parse HTML document
            parser = HTMLParser(workspace)
            soup = await parser.load_document(relative_path)

            # Prepare modifier
            modifier = HTMLModifier(soup)

            # Apply modification based on type
            if modification_type == "replace":
                modified_soup, count = modifier.replace_element_content(selector, new_content, selector_type)
            elif modification_type == "attributes":
                if not attributes:
                    return json.dumps({"error": "No attributes provided for 'attributes' modification"})
                modified_soup, count = modifier.modify_attributes(selector, attributes, selector_type)
            elif modification_type == "insert":
                modified_soup, count = modifier.insert_content(selector, new_content, position, selector_type)
            elif modification_type == "remove":
                modified_soup, count = modifier.remove_elements(selector, selector_type)
            else:
                return json.dumps({"error": f"Unsupported modification type: {modification_type}"})

            # Save modified document if output path provided
            if output_path:
                # Validate output path
                out_error, out_workspace, out_relative_path = self._validate_and_get_workspace_path(output_path)
                if out_error:
                    return json.dumps({"error": f"Invalid output path: {out_error}"})

                # Get the full output path
                full_output_path = out_workspace.full_path(out_relative_path)
                if not full_output_path:
                    return json.dumps({"error": f"Cannot create output path: {output_path}"})

                # Write to the output file
                with open(full_output_path, 'w', encoding='utf-8') as f:
                    f.write(str(modified_soup))

                return json.dumps({
                    "success": True,
                    "message": f"Modified {count} elements and saved to {output_path}"
                })
            else:
                return json.dumps({
                    "success": True,
                    "message": f"Modified {count} elements",
                    "modified_count": count
                })

        except DocExplorerError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            error_msg = f"Error modifying HTML document: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})

    @json_schema(
        "Render HTML content or specific elements in the UI",
        {
            "path": {
                "type": "string",
                "description": "UNC-style path (//WORKSPACE/path) to the HTML file",
                "required": True
            },
            "selector": {
                "type": "string",
                "description": "Optional CSS selector or XPath to choose elements to render",
                "required": False
            },
            "highlight": {
                "type": "string",
                "description": "Optional CSS selector for elements to highlight in the rendered output",
                "required": False
            },
            "selector_type": {
                "type": "string",
                "description": "Type of selector: 'css' or 'xpath'",
                "required": False
            },
            "title": {
                "type": "string",
                "description": "Title for the rendered content",
                "required": False
            }
        }
    )
    async def render(self, **kwargs: Any) -> str:
        """Render HTML content or specific elements in the UI

        Args:
            path: UNC-style path (//WORKSPACE/path) to the HTML file
            selector: Optional CSS selector or XPath to choose elements to render
            highlight: Optional CSS selector for elements to highlight in the rendered output
            selector_type: Type of selector: 'css' or 'xpath' (default: 'css')
            title: Title for the rendered content (default: "HTML Preview")

        Returns:
            Success message after sending RenderMedia event
        """
        try:
            unc_path = kwargs.get("path")
            selector = kwargs.get("selector")
            highlight = kwargs.get("highlight")
            selector_type = kwargs.get("selector_type", "css").lower()
            title = kwargs.get("title", "HTML Preview")

            # Validate path
            error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
            if error:
                return json.dumps({"error": error})

            # Parse HTML document
            parser = HTMLParser(workspace)
            soup = await parser.load_document(relative_path)

            # Extract requested content if selector provided
            if selector:
                selector_engine = SelectorEngine(soup)
                elements = selector_engine.query(selector, selector_type)
                
                if not elements:
                    return json.dumps({
                        "error": f"No elements found matching {selector_type} selector: {selector}"
                    })
                
                # Use the first element or combine multiple elements
                if len(elements) == 1:
                    html_content = str(elements[0])
                else:
                    # Wrap multiple elements in a div for proper rendering
                    html_content = "<div>" + "".join(str(e) for e in elements) + "</div>"
            else:
                # Use the entire document
                html_content = str(soup)

            # Prepare renderer
            renderer = HTMLRenderer()
            render_data = renderer.prepare_render_data(html_content, title, highlight)

            # Send RenderMedia event
            if self.streaming_callback:
                await self.chat_callback(
                    content="Content rendered in UI",
                    meta={"render_media": render_data}
                )
                return json.dumps({
                    "success": True,
                    "message": "HTML content rendered in UI"
                })
            else:
                return json.dumps({
                    "success": True,
                    "message": "No streaming callback available to render content",
                    "render_data": render_data
                })

        except DocExplorerError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            error_msg = f"Error rendering HTML content: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})


# Register the toolset
Toolset.register(DocExplorerTools)
```

## Project Configuration Files

### `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "doc_explorer"
version = "0.1.0"
description = "HTML document exploration and manipulation tool for AI agents"
authors = [
    {name = "Agent C Team", email = "team@agentc.ai"}
]
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

dependencies = [
    "beautifulsoup4>=4.11.0",
    "lxml>=4.9.0",
    "html2text>=2020.1.16",
    "cssselect>=1.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.19.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[tool.black]
line-length = 100
target-version = ['py38']
```

### `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name="doc_explorer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    install_requires=[
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "html2text>=2020.1.16",
        "cssselect>=1.2.0",
    ],
    python_requires=">=3.8",
)
```

## Usage Examples

Here are some examples of how to use the Doc Explorer tool:

### 1. Get Document Structure

```python
from doc_explorer import DocExplorerTools

# Initialize toolset
doc_explorer = DocExplorerTools(...)

# Get structure overview of an HTML file
structure_result = await doc_explorer.structure(
    path="//workspace/site/index.html", 
    max_depth=3
)
```

### 2. Query Elements

```python
# Find all articles with the 'featured' class
articles = await doc_explorer.query(
    path="//workspace/site/index.html",
    selector="article.featured",
    limit=5
)

# Using XPath to find all links with 'download' in their text
download_links = await doc_explorer.query(
    path="//workspace/site/downloads.html",
    selector="//a[contains(text(), 'download')]",
    selector_type="xpath"
)
```

### 3. Convert to Markdown

```python
# Convert main content area to markdown for more efficient analysis
markdown_content = await doc_explorer.to_markdown(
    path="//workspace/site/article.html",
    selector="main.content"
)
```

### 4. Modify HTML

```python
# Replace page title
await doc_explorer.modify(
    path="//workspace/site/index.html",
    selector="title",
    new_content="<title>Updated Site Title</title>",
    output_path="//workspace/site/updated_index.html"
)

# Add a class to all buttons
await doc_explorer.modify(
    path="//workspace/site/form.html",
    selector="button",
    modification_type="attributes",
    attributes={"class": "styled-button"},
    output_path="//workspace/site/updated_form.html"
)

# Remove all script tags
await doc_explorer.modify(
    path="//workspace/site/index.html",
    selector="script",
    modification_type="remove",
    output_path="//workspace/site/clean_index.html"
)
```

### 5. Render HTML in UI

```python
# Render a specific article with code blocks highlighted
await doc_explorer.render(
    path="//workspace/site/tutorial.html",
    selector="article.tutorial",
    highlight="pre, code",
    title="Tutorial Content"
)
```