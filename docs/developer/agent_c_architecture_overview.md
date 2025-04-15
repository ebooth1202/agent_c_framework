# Agent C Core Architecture Overview

## 1. Overall Architecture

Agent C is a thin abstraction layer over chat completion APIs (OpenAI, Anthropic, etc.) that provides a structured framework for building AI agents. The system follows a modular architecture with several key components:

```
┌─────────────────┐      ┌──────────────────┐      ┌───────────────────┐
│                 │      │                  │      │                   │
│   Agent Layer   │─────▶│  Prompt System   │─────▶│   LLM Providers   │
│                 │      │                  │      │                   │
└────────┬────────┘      └──────────────────┘      └───────────────────┘
         │                                                    ▲
         │                                                    │
         ▼                                                    │
┌─────────────────┐      ┌──────────────────┐                │
│                 │      │                  │                │
│  Tooling System │◀─────│  Event System   │◀───────────────┘
│                 │      │                  │
└─────────────────┘      └─────────┬────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │                  │
                          │ Session Manager  │
                          │                  │
                          └──────────────────┘
```

## 2. Key Subsystems

### 2.1 Agent Layer

The agent layer provides the core abstractions for interacting with LLM providers:

- `BaseAgent`: An abstract base class that defines the common interface for all agents
- Implementation-specific agents (e.g., `ClaudeAgent`, `GPTAgent`) that handle provider-specific details
- Supports both stateless (one-shot) and stateful (chat) interactions
- Handles functionality like token counting, retrying, and error handling

### 2.2 Prompt System

The prompt system provides a structured way to build and manage prompts:

- `PromptBuilder`: Composable prompt builder that assembles different prompt sections
- `PromptSection`: Modular prompt components (persona, tools, safety, etc.)
- Support for template variables and context-specific rendering

### 2.3 Chat & Session Management

Handles user sessions and chat history:

- `ChatSessionManager`: Abstract interface for session management
- `ZepCESessionManager`: Concrete implementation using Zep for persistence
- Tracks chat history, user metadata, and session state
- Currently marked as needing an overhaul to better leverage Zep's capabilities

### 2.4 Tooling System

Provides mechanisms for agents to interact with external tools and services:

- `ToolSet`: Collection of related tools grouped by namespace
- `ToolChest`: Container for multiple toolsets
- `MCPToolset`/`MCPToolChest`: Implementations that support the MCP protocol for tool interoperability
- `MCPToolChestServer`: Allows exposing ToolChests through the MCP protocol to other systems

### 2.5 Event System

Provides a callback and event mechanism for asynchronous interactions:

- `ObservableModel`: Base class for observable entities
- `ChatEvent`: Core event type for chat-related activities
- Specialized event types: `InteractionEvent`, `CompletionEvent`, `TextDeltaEvent`, etc.
- Currently a stand-in for what would be a queue-based system in production

## 3. Interaction Flows

### 3.1 Basic Chat Flow

1. User sends a message through a client interface
2. Agent processes the message, potentially using the session history
3. Agent generates a prompt using the PromptBuilder system
4. Agent sends the prompt to the LLM provider
5. Provider response is processed and returned through events
6. Session manager updates chat history

### 3.2 Tool Usage Flow

1. Agent identifies a need to use a tool during message processing
2. Agent calls the tool via ToolChest
3. Tool execution results are returned to the Agent
4. Agent incorporates tool results into its response
5. Tool use and results are captured in events and session history

## 4. Implementation Notes

### 4.1 Current Limitations & Planned Improvements

- **Chat Callback System**: Currently in-process; intended to be replaced with a queue-based system for decoupling components
- **Session Manager**: Needs overhaul to properly leverage Zep's capabilities
- **Event System**: Intended to be more robust for production use

### 4.2 Design Patterns

- **Observer Pattern**: Used extensively in the event system via `ObservableModel`
- **Adapter Pattern**: Used in tool integration, especially for MCP protocol
- **Builder Pattern**: Used in the prompt construction system
- **Strategy Pattern**: Different agent implementations for different LLM providers

## 5. Development Considerations

### 5.1 Extensibility Points

- Adding new tool sets
- Implementing new agent types for different LLM providers
- Creating custom prompt sections
- Extending event types for new interaction patterns

### 5.2 Future Direction

- Replacement of in-process callbacks with queue-based architecture
- Better separation of concerns between components
- Improved session management with proper Zep integration
- Enhanced tooling system with better security and access control