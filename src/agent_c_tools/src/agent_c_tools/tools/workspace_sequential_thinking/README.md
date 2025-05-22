# Workspace Sequential Thinking Tools

## Overview

The Workspace Sequential Thinking Tools provide a structured approach to thinking through complex problems step-by-step. This toolset helps agents break down problems, revise their thinking, and explore alternative paths of reasoning using a sequential thinking process.

## Features

- **Structured Thinking**: Break down complex problems into numbered thought steps
- **Revisable Thoughts**: Update previous thoughts when new information emerges
- **Branching Paths**: Explore alternative thinking approaches through branches
- **Persistent Storage**: Store thinking processes in workspace metadata for long-term access
- **Context Tracking**: Maintain context across multiple thinking steps

## When to Use

1. Breaking down complex problems into steps
2. Planning and design with room for revision
3. Analysis that might need course correction
4. Problems where the full scope might not be clear initially
5. Tasks that need to maintain context over multiple steps
6. Situations where irrelevant information needs to be filtered out

## Usage

To use the Workspace Sequential Thinking Tools in your agent:

1. Create a new sequential thinking process:

```python
result = await tool_chest.call("wst-create_thinking", {
    "thinking_path": "//project/problem_analysis",
    "title": "Complex Problem Analysis",
    "description": "Breaking down and analyzing a complex issue"
})
```

2. Add thoughts to the process:

```python
result = await tool_chest.call("wst-add_thought", {
    "thinking_path": "//project/problem_analysis",
    "thought": "First, I need to understand the core requirements...",
    "thought_number": 1,
    "total_thoughts": 5,
    "next_thought_needed": True
})
```

3. Add a thought that revises a previous one:

```python
result = await tool_chest.call("wst-add_thought", {
    "thinking_path": "//project/problem_analysis",
    "thought": "On further reflection, the requirements actually suggest...",
    "thought_number": 3,
    "total_thoughts": 5,
    "next_thought_needed": True,
    "is_revision": True,
    "revises_thought": 1
})
```

4. Create a branch to explore an alternative approach:

```python
result = await tool_chest.call("wst-create_branch", {
    "thinking_path": "//project/problem_analysis",
    "parent_thought_number": 2,
    "name": "Alternative Approach",
    "description": "Exploring a different solution strategy"
})

# Add a thought to the branch
result = await tool_chest.call("wst-add_thought", {
    "thinking_path": "//project/problem_analysis",
    "thought": "What if we approached this from a different angle...",
    "thought_number": 3,
    "total_thoughts": 6,
    "next_thought_needed": True,
    "branch_from_thought": 2,
    "branch_id": "branch-id-from-create-branch-result"
})
```

5. List all thoughts in the process:

```python
result = await tool_chest.call("wst-list_thoughts", {
    "thinking_path": "//project/problem_analysis",
    "include_content": True
})
```

## Implementation Details

The Workspace Sequential Thinking Tools use the workspace metadata system to store thinking processes, which provides several benefits:

- **Persistence**: Thinking processes persist across sessions
- **Integration**: Thinking processes are associated with relevant workspaces
- **Accessibility**: Simple path-based access using `//workspace/thinking_id` format
- **Efficiency**: Lightweight storage with minimal overhead

## Data Models

- **ThoughtModel**: Represents a single thought in the process
- **ThoughtBranchModel**: Represents a branch of alternative thinking
- **SequentialThinkingModel**: The top-level model containing thoughts and branches

## Recommended Approach

1. Start with an initial estimate of needed thoughts
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Only set next_thought_needed to false when truly done