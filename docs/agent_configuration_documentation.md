# Agent Configuration System

## Overview

The Agent Configuration system defines how individual agents are configured and how they collaborate within the Agent C framework. Agent configurations appear in several contexts within the realtime API:

- **Session Events**: `AgentListEvent` provides available agent configurations
- **Chat Sessions**: Agent configurations determine behavior and capabilities
- **Subsessions**: Agent-to-agent conversations use these configurations
- **Team Collaboration**: The category system enables sophisticated agent teamwork

## CurrentAgentConfiguration Model

The `CurrentAgentConfiguration` model (version 2) defines the complete structure of an agent configuration:

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | `int` | Configuration version (currently 2) |
| `key` | `string` | Unique identifier for the agent configuration |
| `name` | `string` | Human-readable name of the agent |
| `agent_description` | `string?` | Optional description of the agent's purpose and capabilities |
| `model_id` | `string` | ID of the LLM model used by the agent |
| `persona` | `string` | Core instructions that define the agent's behavior |
| `uid` | `string?` | Optional unique identifier in slug form |

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `agent_params` | `CompletionParams?` | Optional LLM interaction parameters |
| `prompt_metadata` | `object?` | Metadata for prompt generation and variable substitution |
| `tools` | `string[]` | List of enabled toolset names the agent can use |
| `blocked_tool_patterns` | `string[]` | Patterns for blocking specific tools (e.g., `"run_*"`) |
| `allowed_tool_patterns` | `string[]` | Patterns that override blocks (e.g., `"run_git"`) |
| `category` | `string[]` | List of categories from most to least general |

## Agent Category System

The category system is critical for understanding agent behavior and collaboration patterns. Categories serve multiple purposes:

### Special Category Meanings

#### `'domo'` - User Collaboration Agents
- Agents designed for direct interaction with users
- Include human interaction rules and safety guidelines
- Optimized for conversational interfaces
- Can handle user requests and provide assistance

#### `'realtime'` - Voice-Optimized Agents  
- Specifically optimized for voice conversation
- **Always include `'domo'` as a category** (all realtime agents are also domos)
- Tuned for natural speech patterns and real-time interaction
- Include voice-specific behavioral guidelines

#### `'assist'` - Agent Helper Agents
- Designed to help other agents, not end users
- **Lack human interaction rules and safety guidelines**
- Exposed via the `AgentAssistTool` for agent-to-agent communication
- Focused on specific technical tasks or capabilities

### Team Formation Through Categories

When an agent key appears in another agent's categories, it creates a **team relationship**:

```json
{
  "key": "agent_b",
  "name": "Agent B",
  "category": ["agent_a", "assist"],
  // ... other fields
}
```

In this example:
- `agent_b` is part of `agent_a`'s team
- `agent_a` can use `AgentTeamTools` to communicate with `agent_b`
- This enables sophisticated multi-agent collaboration patterns

## Completion Parameters

The `agent_params` field contains provider-specific parameters for LLM interactions. The system supports multiple LLM providers through a discriminated union:

### Parameter Types

#### Claude Parameters

**Non-Reasoning (claude_non_reasoning)**:
```json
{
  "type": "claude_non_reasoning",
  "model_name": "claude-3-5-sonnet-latest",
  "max_tokens": 4000,
  "temperature": 0.7,
  "user_name": "developer",
  "auth": {
    "api_key": "sk-..."
  }
}
```

**Reasoning (claude_reasoning)**:
```json
{
  "type": "claude_reasoning", 
  "model_name": "claude-4-sonnet-latest",
  "max_tokens": 2000,
  "budget_tokens": 8000,
  "max_searches": 3,
  "user_name": "developer"
}
```

#### GPT Parameters

**Non-Reasoning (g_p_t_non_reasoning)**:
```json
{
  "type": "g_p_t_non_reasoning",
  "model_name": "gpt-4o",
  "max_tokens": 4000,
  "temperature": 0.7,
  "presence_penalty": 0.1,
  "stop": ["END"],
  "seed": 42,
  "voice": "alloy"
}
```

**Reasoning (g_p_t_reasoning)**:
```json
{
  "type": "g_p_t_reasoning",
  "model_name": "gpt-4o",
  "max_tokens": 2000,
  "reasoning_effort": "medium",
  "temperature": 0.5
}
```

### Common Parameters

All completion parameter types include these common fields:

- `model_name`: The specific LLM model to use
- `max_tokens`: Maximum tokens to generate (optional)
- `user_name`: Name of the user interacting with the agent (optional)
- `auth`: Authentication information for the LLM provider (optional)

## Example Configurations

### Voice-Optimized User Agent

```json
{
  "version": 2,
  "key": "friendly_assistant",
  "name": "Friendly Assistant",
  "agent_description": "A helpful voice-enabled assistant for general user support",
  "model_id": "gpt-4o-realtime",
  "persona": "You are a friendly, helpful assistant optimized for voice conversation...",
  "category": ["realtime", "domo", "general"],
  "tools": ["web_search", "calculator"],
  "agent_params": {
    "type": "g_p_t_non_reasoning",
    "model_name": "gpt-4o",
    "voice": "alloy",
    "temperature": 0.8
  }
}
```

### Technical Assistant Agent

```json
{
  "version": 2,
  "key": "code_helper",
  "name": "Code Helper",
  "agent_description": "Specialized assistant for code analysis and technical tasks",
  "model_id": "claude-3-5-sonnet",
  "persona": "You are a technical assistant specializing in code analysis...",
  "category": ["lead_developer", "assist", "technical"],
  "tools": ["code_analysis", "git_tools"],
  "blocked_tool_patterns": ["run_*"],
  "allowed_tool_patterns": ["run_git", "run_pytest"],
  "agent_params": {
    "type": "claude_non_reasoning",
    "model_name": "claude-3-5-sonnet-latest",
    "temperature": 0.3
  }
}
```

### Team Leader Agent

```json
{
  "version": 2,
  "key": "lead_developer", 
  "name": "Lead Developer",
  "agent_description": "Senior developer agent that coordinates with team members",
  "model_id": "claude-3-5-sonnet",
  "persona": "You are a senior developer who coordinates with your team...",
  "category": ["domo", "technical", "leadership"],
  "tools": ["code_review", "agent_team_tools", "project_management"],
  "agent_params": {
    "type": "claude_non_reasoning",
    "model_name": "claude-3-5-sonnet-latest",
    "temperature": 0.5
  }
}
```

## Client Implementation Notes

### Category-Based Behavior

When implementing clients, consider category-based behavior:

- **`domo` agents**: Can be exposed directly to users in chat interfaces
- **`realtime` agents**: Should be preferred for voice interaction features
- **`assist` agents**: Should not be exposed directly to end users
- **Team relationships**: Agents with other agent keys in their categories are part of those agents' teams

### Tool Filtering

Agents automatically filter available tools based on their patterns:
1. Tools matching `blocked_tool_patterns` are removed
2. Tools matching `allowed_tool_patterns` are restored (overrides blocks)
3. This allows fine-grained control over agent capabilities

### Session Context

Agent configurations appear in:
- **Initial connection**: `AgentListEvent` provides all available agents
- **Session changes**: When agents switch during conversation
- **Subsessions**: Agent-to-agent conversations use separate configurations
- **Team interactions**: When agents collaborate using team tools

Understanding these configurations is essential for building clients that can effectively display agent capabilities, handle voice interactions, and visualize complex multi-agent collaboration patterns.