# Agent C Toolsets Framework

## Overview

The Agent C Toolsets framework provides a structured way to create, manage, and use tools within AI agents. The framework emphasizes composability, tool integration, and practical implementation. This document serves as context information for developing agent model instructions that leverage the toolsets system.

## Key Components

### Toolset

A `Toolset` is a collection of related tools that can be used by an agent. Each toolset:

- Has a unique name
- Contains one or more methods decorated with `json_schema`
- Can define requirements for its usage (environment variables, dependencies)
- Can stream events back to the agent or user interface
- Can access a shared tool cache for persistent storage

### ToolChest

The `ToolChest` manages the registration, activation, and access to multiple toolsets. It:

- Maintains a registry of available toolset classes
- Initializes toolset instances with proper dependencies
- Provides access to active tools for the agent
- Generates schema representations for different LLM formats (OpenAI, Claude)
- Manages tool-related prompt sections for agent instructions

### ToolCache

The `ToolCache` provides persistent storage capabilities for toolsets, allowing them to:

- Store and retrieve data between invocations
- Set expiration times for cached data
- Share data between different toolsets
- Maintain state across agent interactions

### JSON Schema Decorator

The `json_schema` decorator is used to annotate toolset methods, transforming them into tools that can be:

- Exposed to LLMs in their function-calling interfaces
- Properly documented with descriptions and parameter details
- Validated for required parameters

## Toolset Registration and Activation

### Registration Process

Toolsets are registered through the `Toolset.register()` class method:

```python
from agent_c.toolsets.tool_set import Toolset

class MyToolset(Toolset):
    # Toolset implementation
    pass

# Register the toolset
Toolset.register(MyToolset)
```

### Activation Process

Toolsets are activated during the initialization of the ToolChest:

1. The `ToolChest.init_tools()` method is called
2. Each registered toolset class is instantiated with necessary dependencies
3. Successfully initialized toolsets are added to the active tools
4. Each toolset's `post_init()` method is called for additional setup

## Creating Custom Toolsets

### Basic Structure

```python
from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema

class ExampleToolset(Toolset):
    def __init__(self, **kwargs):
        # Required: call the parent constructor with all kwargs
        super().__init__(**kwargs)
        
        # Optional: perform additional initialization
        self.my_custom_property = "some value"
    
    @json_schema(
        description="Does something useful",
        params={
            "param1": {
                "type": "string",
                "description": "A string parameter",
                "required": True
            },
            "param2": {
                "type": "integer",
                "description": "An optional integer parameter"
            }
        }
    )
    async def do_something(self, param1, param2=None):
        # Tool implementation
        result = f"Did something with {param1}"
        if param2:
            result += f" and {param2}"
        return result
    
    async def post_init(self):
        # Optional: perform initialization that requires
        # other toolsets to be available
        pass

# Register the toolset
Toolset.register(ExampleToolset)
```

### Toolset Events

Toolsets can raise different types of events during execution:

- `_raise_message_event`: Send a complete message
- `_raise_text_delta_event`: Send incremental text updates
- `_raise_render_media`: Send rich media (images, charts, etc.)

### Using ToolCache

Toolsets can use the tool cache for persistent storage:

```python
# Store a value
self.tool_cache.set("my_key", my_value)

# Retrieve a value
stored_value = self.tool_cache.get("my_key")

# Store with expiration (in seconds)
self.tool_cache.set("temporary_key", temp_value, expire=3600)  # 1 hour
```

## Integration with Agent Instructions

### Available Tools

When creating agent instructions, you can reference the active toolsets and their capabilities:

```
This agent has access to the following toolsets:

1. {{toolset_name}}: {{toolset_description}}
   - {{tool_name}}: {{tool_description}}
   - {{tool_name}}: {{tool_description}}

2. {{another_toolset}}: {{toolset_description}}
   - {{tool_name}}: {{tool_description}}
```

### Tool Usage Guidelines

Provide clear guidelines on when and how to use the available tools:

```
When using tools, follow these guidelines:

1. Choose the appropriate toolset based on the task requirements
2. Provide all required parameters
3. Handle errors gracefully
4. Use the tool results to inform your responses
```

### Tool Naming Convention

Tools are named using the convention `{toolset_name}-{method_name}`, for example:

- `file_system-read_file`
- `web_search-find_results`
- `calculator-add_numbers`

This naming convention helps organize tools by their functionality and prevents naming conflicts.

## Best Practices

1. **Toolset Organization**: Group related tools within the same toolset
2. **Clear Documentation**: Provide detailed descriptions and parameter information
3. **Error Handling**: Include robust error handling within tool implementations
4. **Appropriate Caching**: Use the tool cache strategically for improved performance
5. **Stateless Design**: When possible, design tools to be stateless for better reliability
6. **Streaming for Long Operations**: Use streaming events for tools that take substantial time
7. **Environment Validation**: Check for required environment variables or dependencies
8. **Logical Naming**: Use clear, descriptive names for toolsets and tools