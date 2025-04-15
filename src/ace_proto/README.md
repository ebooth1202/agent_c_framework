# Code Explorer PROTOTYPE

This is a prootype of a real tool that's coming toon

## Features

- **String-Based Processing**: Works directly with code strings, no file operations required
- **Multi-Language Support**: Designed for multiple languages (currently Python, with more coming soon)
- **Smart Extraction**: Extract only what you need - public interfaces, specific entities, etc.
- **Different Detail Levels**: Get just the information you need - from high-level summaries to full source code
- **AI-Friendly Output**: Results available in dict, JSON, or Markdown formats

## Installation

Requires Python 3.7+ and tree-sitter:

```bash
pip install tree-sitter
```

For each language you want to support, install the corresponding tree-sitter language package:

```bash
pip install tree-sitter-python  # For Python support
# pip install tree-sitter-javascript  # For JavaScript support (coming soon)
```

## Quick Start

```python
from ts_tool import api

# Example code to analyze
code = """
class MyClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        """Return the stored value."""
        return self.value

def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)
"""

# Get a high-level summary of the code
summary = api.get_code_summary(code, format='dict')
print(f"Classes: {summary['class_count']}, Functions: {summary['function_count']}")

# Get the public interface
interface = api.get_public_interface(code, format='markdown')
print(interface)

# Get a specific class with full source code
class_info = api.get_entity(code, 'class', 'MyClass', detail_level='full', format='dict')
print(class_info['source_code'])

# Get a specific method's signature
signature = api.get_signature(code, 'method', 'MyClass.get_value')
print(signature)

# Get documentation for a function
doc = api.get_documentation(code, 'function', 'calculate_sum')
print(doc)  # "Calculate sum of numbers."
```

## API Reference

### Core Functions

- `get_supported_languages()`: Get list of supported languages
- `detect_language(code, filename=None)`: Detect the language of code
- `get_code_summary(code, language=None, filename=None, format='dict')`: Get summary of code structure
- `get_public_interface(code, language=None, filename=None, format='dict')`: Get public interface elements
- `get_entity(code, entity_type, entity_name, detail_level='full', language=None, filename=None, format='dict')`: Get specific entity
- `explore_code(code, language=None, filename=None, format='dict')`: Get complete code structure

### Convenience Functions

- `get_source_code(code, entity_type, entity_name, language=None, filename=None)`: Get source code for entity
- `get_signature(code, entity_type, entity_name, language=None, filename=None)`: Get signature for entity
- `get_documentation(code, entity_type, entity_name, language=None, filename=None)`: Get documentation for entity

## Detail Levels

Three detail levels are available:

- `summary`: Basic information about the entity (name, location, etc.)
- `signature`: Entity signature (class/function/method signature)
- `full`: Complete source code of the entity

## Output Formats

Three output formats are supported:

- `dict`: Python dictionary (default)
- `json`: JSON string
- `markdown`: Formatted Markdown string

## Entity Types

Supported entity types:

- `class`: Class definitions
- `function`: Standalone functions
- `method`: Class methods (use format 'ClassName.method_name')
- `variable`: Variables and constants
- `module`: Entire module (only for some operations)

## Examples

See the `examples` directory for comprehensive usage examples.

## License

MIT