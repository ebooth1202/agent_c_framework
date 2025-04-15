# Creating Tools with Tim: A Developer's Guide to Agent C Tools

## Introduction: Why Build Tools for AI Agents?

If you've been watching the AI space with a mix of fascination and trepidation, you're not alone. As developers, we're seeing rapid changes in how software is built and used. The question isn't whether AI will impact your career—it's *how you'll adapt to stay relevant*.

Building tools for AI agents represents one of the most valuable skills you can develop right now. Think of it this way: AI agents are like new junior developers who can work 24/7, don't complain about meetings, and learn incredibly fast. But they need tools to be truly effective—and that's where you come in.

> "Give me six hours to chop down a tree and I will spend the first four sharpening the axe." — Abraham Lincoln

Tools are the axes that make AI agents effective. Without well-designed tools, even the most sophisticated AI is limited to what it can do with text alone. By creating tools, you're essentially becoming the architect who determines what these systems can accomplish.

## What Are Agent C Tools?

Before diving into the technical details, let's understand what we mean by "tools" in the Agent C framework:

**Tools** are specialized functions that extend an AI agent's capabilities beyond generating text. They allow agents to:

- Access external systems (databases, APIs, file systems)
- Perform calculations
- Transform data
- Execute code
- Interact with the physical world (through IoT devices, robotics interfaces, etc.)

Consider this analogy: if an AI agent is like a brain, tools are like sensory organs and limbs that let it perceive and interact with the world.

In Agent C, tools are organized into **Toolsets**—logical groupings of related tools. For example:
- A `FileSystem` toolset might contain tools for reading, writing, and listing files
- A `WebSearch` toolset might provide tools for querying search engines and fetching results
- A `Calculator` toolset could offer mathematical operations

## Meet Tim: Your Guide to Tool Development

Tim (affectionately known as "Tim the Tool Man") is an AI assistant specifically designed to help you create high-quality tools for the Agent C framework. Tim combines:

- Deep technical knowledge of the Agent C codebase
- Practical software development expertise
- A straightforward, hands-on approach to problem-solving

Think of Tim as the experienced senior developer who's been tasked with helping you get up to speed. He:
- Speaks in plain language, not jargon
- Provides practical examples rather than just theory
- Helps you write clean, maintainable code
- Guides you through testing and debugging

Tim is part of the "Conway" class of enhanced reasoning agents, which means he takes time to think through problems thoroughly before proposing solutions—just like a good developer should.

## Creating Your First Tool: A Step-by-Step Guide

### 1. Understanding the Problem Space

Before writing a single line of code, you need clarity on what your tool should accomplish. Work with Tim to answer these questions:

- What specific capability are you adding to the agent?
- What inputs will your tool need?
- What outputs should it produce?
- Are there existing libraries or services you can leverage?
- What error conditions should you handle?

### 2. Setting Up Your Development Environment

Agent C tools are written in Python. At minimum, you'll need:

- Python 3.12 installed
- The Agent C project cloned locally
- Access to the `tools` workspace
  - Create an entry in `.localworkspaces.json` that maps to the `src/agent_c_tool` sub folder of this repo and name it `tools`

Tim can help you validate your setup and troubleshoot any issues.

### 3. Creating a New Toolset

If your tool fits into an existing toolset, you can extend that. Otherwise, you'll create a new toolset class:

```python
from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema

class MyNewToolset(Toolset):
    """My new toolset that does something awesome."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize any resources or connections your tools will need
        
    async def post_init(self):
        # Optional: perform setup that requires other toolsets to be initialized
        pass
```

### 4. Defining Your Tool Methods

Each method decorated with `@json_schema` becomes a tool that agents can use:

```python
@json_schema(
    description="Does something useful with the provided information",
    params={
        "input_text": {
            "type": "string",
            "description": "The text to process",
            "required": True
        },
        "options": {
            "type": "object",
            "description": "Optional configuration parameters"
        }
    }
)
async def do_something_useful(self, input_text, options=None):
    """Process the input text according to specified options."""
    # Tool implementation goes here
    result = f"Processed: {input_text}"
    return result
```

### 5. Registering Your Toolset

At the end of your module, register your toolset so it can be discovered:

```python
# Register the toolset
Toolset.register(MyNewToolset)
```

### 6. Testing Your Tool

Testing is crucial for tool development. You can create unit tests or use the Agent C CLI to test your tools directly:

```python
# Example test code with pytest
def test_my_tool():
    toolset = MyNewToolset()
    result = await toolset.do_something_useful("test input")
    assert "Processed: test input" in result
```

## Working with Tim: Practical Collaboration

When developing tools with Tim, you'll follow a collaborative workflow:

1. **Describe your goal**: Explain what you want your tool to accomplish
2. **Refine the requirements**: Tim will ask clarifying questions
3. **Design the solution**: Work together to outline the approach
4. **Implement incrementally**: Build and test in small steps
5. **Review and refine**: Improve code quality and handle edge cases

Tim uses a scratchpad (located at `//tools/.scratch`) to keep track of your progress and plan. You can always ask him to check the scratchpad to get back up to speed on your project.

### Example Interaction

```
You: Tim, I need to create a tool that can extract tabular data from PDF files.

Tim: That's a practical tool that could save agents a lot of hassle! Let me ask a few questions:
1. What format should the extracted data be in? (JSON, CSV, etc.)
2. Do you need to specify which pages or tables to extract?
3. Are there any specific PDF libraries you prefer to use?

You: I'd like the data in JSON format. Users should be able to specify page ranges. I don't have a preference for libraries.

Tim: Great! Let's create a plan for this tool...
```

## Beyond the Basics: Advanced Tool Features

Once you're comfortable with basic tool creation, you can explore advanced features:

### Using ToolCache for Persistence

Tools can store and retrieve data between invocations:

```python
# Store a value
self.tool_cache.set("my_key", my_value)

# Retrieve a value
stored_value = self.tool_cache.get("my_key")

# Store with expiration (in seconds)
self.tool_cache.set("temporary_key", temp_value, expire=3600)  # 1 hour
```

### Streaming Events

For long-running operations, you can stream progress updates:

```python
async def process_large_dataset(self, dataset_path):
    # Start processing
    self._raise_message_event("Starting to process dataset")
    
    # Update progress periodically
    for i in range(10):
        await asyncio.sleep(1)  # Simulate work
        self._raise_text_delta_event(f"Processing batch {i+1}/10\n")
    
    # Return final result
    return "Processing complete!"
```

### Environment Requirements

Specify dependencies your toolset needs:

```python
class WeatherToolset(Toolset):
    # Declare required environment variables
    REQUIRED_ENV_VARS = ["WEATHER_API_KEY"]
    
    # Declare required Python packages
    REQUIRED_PACKAGES = ["requests>=2.25.0"]
```

## Building a Career with AI Tool Development

Let's address the elephant in the room: Many developers worry that AI will replace their jobs. The reality is more nuanced—AI is changing the landscape, but creating immense opportunities for those who adapt.

Developing tools for AI systems positions you at the intersection of traditional development and AI capabilities. You become the bridge between what AI can theoretically do and what it can practically accomplish.

Consider these career advantages:

1. **High-value skills**: Tool developers extend AI capabilities in ways that pure prompt engineering cannot
2. **Domain application**: You can apply your existing domain expertise to create tools for specific industries
3. **Job security**: The ability to create custom tools will remain valuable even as base AI models improve
4. **Transferable knowledge**: The concepts behind tool development apply across different AI frameworks

The developers who thrive in the AI era won't be those who compete with AI at its strengths, but those who amplify their own strengths by leveraging AI effectively. Tool development is one of the clearest paths to becoming that kind of developer.

## Getting Started Today

Ready to begin working with Tim? Here's how to get started:

1. Access the Agent C Web UI and select Tim from the persona dropdown
2. Tell him what kind of tool you'd like to build
3. Be prepared to collaborate—Tim will ask questions to understand your requirements
4. Start small with a focused tool before moving to more complex projects

Remember that tool development is an iterative process. Your first tools might be simple, but as you gain experience, you'll be able to create increasingly sophisticated capabilities for your agents.

## Conclusion: Tools as Career Insurance

The ability to build tools for AI agents isn't just a technical skill—it's career insurance in a rapidly changing landscape. By becoming proficient at extending what AI can do, you position yourself as someone who enhances these systems rather than being replaced by them.

Tim is here to help you develop this skill, combining your domain knowledge with his technical expertise. Together, you can create tools that make AI agents more capable, more useful, and more aligned with human needs.

Whatever your current level of experience with AI, remember this: The best time to start building AI tools was a year ago. The second-best time is today.