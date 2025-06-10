import re
import json
from typing import Dict, Any


class JavaScriptSafeContentProcessor:
    """Pre-processes markdown content to be safe for JavaScript template literals."""

    def __init__(self):
        # Patterns that need escaping for JavaScript safety
        self.escape_patterns = [
            # C# interpolated strings: $"..." -> &#36;"..."
            (r'\$"', '&#36;"'),
            # Template literal expressions: ${...} -> &#36;&#123;...&#125;
            (r'\$\{', '&#36;&#123;'),
            (r'\}', '&#125;'),
            # Backticks: ` -> &#96;
            (r'`', '&#96;'),
            # Script tag components to prevent injection
            (r'</script>', '&#60;/script&#62;'),
            (r'<script>', '&#60;script&#62;'),
        ]

    def escape_javascript_conflicts(self, content: str) -> str:
        """Escape patterns that could conflict with JavaScript template literals."""
        for pattern, replacement in self.escape_patterns:
            content = re.sub(pattern, replacement, content)
        return content

    def process_markdown_content(self, content: str) -> str:
        """Process markdown content to be JavaScript-safe while preserving readability."""
        # Only escape content within code blocks to preserve markdown formatting
        return self._process_code_blocks(content)

    def _process_code_blocks(self, content: str) -> str:
        """Process only code blocks to escape JavaScript conflicts."""
        lines = content.split('\n')
        processed_lines = []
        in_code_block = False
        code_fence_pattern = re.compile(r'^```(\w+)?')

        for line in lines:
            # Check for code fence start/end
            fence_match = code_fence_pattern.match(line.strip())

            if fence_match:
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    processed_lines.append(line)
                else:
                    # Ending a code block
                    in_code_block = False
                    processed_lines.append(line)
            elif in_code_block:
                # We're inside a code block - escape problematic patterns
                escaped_line = self.escape_javascript_conflicts(line)
                processed_lines.append(escaped_line)
            else:
                # Regular markdown - leave as is
                processed_lines.append(line)

        return '\n'.join(processed_lines)

    # def process_file_structure(self, file_structure: list) -> list:
    #     """Process an entire file structure to make all content JavaScript-safe."""
    #     return self._process_structure_recursive(file_structure)
    #
    # def _process_structure_recursive(self, items: list) -> list:
    #     """Recursively process all items in the structure."""
    #     processed_items = []
    #
    #     for item in items:
    #         if item.get('type') == 'file' and 'content' in item:
    #             # Process file content
    #             processed_item = item.copy()
    #             processed_item['content'] = self.process_markdown_content(item['content'])
    #             processed_items.append(processed_item)
    #         elif item.get('type') == 'folder' and 'children' in item:
    #             # Recursively process folder children
    #             processed_item = item.copy()
    #             processed_item['children'] = self._process_structure_recursive(item['children'])
    #             processed_items.append(processed_item)
    #         else:
    #             # Leave other items unchanged
    #             processed_items.append(item)
    #
    #     return processed_items
    #
    # def safe_json_encode(self, data: Any) -> str:
    #     """Safely encode data to JSON with proper escaping."""
    #     # First process the data structure
    #     if isinstance(data, list):
    #         processed_data = self.process_file_structure(data)
    #     elif isinstance(data, dict) and 'content' in data:
    #         processed_data = data.copy()
    #         processed_data['content'] = self.process_markdown_content(data['content'])
    #     else:
    #         processed_data = data
    #
    #     # Then encode to JSON with ensure_ascii=False to preserve Unicode
    #     return json.dumps(processed_data, ensure_ascii=False, separators=(',', ':'))