# Agent C Realtime API Integration Guide

This guide provides practical examples and patterns for integrating with the Agent C Realtime API. It includes working code examples and best practices for building robust clients.

## Prerequisites

- Valid JWT token for authentication
- WebSocket client library
- Basic understanding of event-driven programming

## Event System Architecture

The Agent C Realtime API uses a sophisticated event system built on a BaseEvent inheritance hierarchy. Understanding this architecture is crucial for proper integration.

### BaseEvent Foundation

All events in the system inherit from the `BaseEvent` base class:

```python
class BaseEvent(BaseModel):
    type: str  # Auto-generated from class name
```

**Key Features:**
- **Automatic Type Generation**: The `type` field is automatically set to the snake_case version of the class name with the "Event" suffix removed
- **Auto-Registration**: All event classes automatically register themselves when defined
- **Pydantic Integration**: Built on Pydantic BaseModel for robust validation

**Event Type Naming Convention:**
- Class: `InteractionEvent` → Type: `"interaction"`
- Class: `TextDeltaEvent` → Type: `"text_delta"`
- Class: `CompletionEvent` → Type: `"completion"`

### Event Categories

There are two distinct categories of events in the system:

#### 1. Control Events

Control events handle API configuration and system control. They inherit directly from `BaseEvent` and do not have session context.

**Common Control Events:**
- `get_agents` - Request available agents list
- `set_agent` - Configure the active agent
- `text_input` - Send user text input
- `set_avatar` - Configure avatar session
- `error` - System error notifications
- `ping`/`pong` - Connection health checks

**Control Event Structure:**
```javascript
{
    "type": "set_agent",
    "agent_key": "helpful_assistant"
}
```

#### 2. Session Events

Session events are generated within chat sessions and always include session context. They inherit from `SessionEvent` which extends `BaseEvent`.

**Session Event Structure:**
```javascript
{
    "type": "text_delta",
    "session_id": "sess_abc123",
    "role": "assistant",
    "parent_session_id": null,  // Optional: parent session for nested sessions
    "user_session_id": "user_sess_xyz789",  // Optional: top-level user session
    "content": "Hello, how can I help you?",
    "format": "markdown"
}
```

**Session ID Correlation System:**
- `session_id`: Current session identifier (required)
- `role`: Role that triggered the event (required)
- `parent_session_id`: Parent session ID for nested/child sessions (optional)
- `user_session_id`: Top-level user session for hierarchy tracking (optional)

This correlation system enables:
- Multi-user environment routing based on session_id
- Session hierarchy management for complex interactions
- Proper event attribution in nested agent conversations

### Key Session Event Types

#### Interaction Management
- `interaction` - Marks the start/end of agent interactions
- `completion` - Tracks LLM completion lifecycle and token usage

#### Content Streaming
- `text_delta` - Incremental text content chunks
- `thought_delta` - Agent thinking process (when available)
- `complete_thought` - Final thought content for non-delta clients

#### System Communication
- `system_message` - System notifications to users (errors, warnings, info)
- `message` - Complete text-based messages
- `system_prompt` - System prompt updates (for logging/quality)

#### History Management
- `history` - Complete message history in vendor format
- `history_delta` - Newly added messages only

#### Media and Rich Content
- `render_media` - Display media content with security controls

#### Session Management
- `subsession_started` - Nested session initiation
- `subsession_ended` - Nested session completion

### Security Considerations

#### RenderMedia Event Security

The `render_media` event includes a critical security field:

```javascript
{
    "type": "render_media",
    "content_type": "image/png",
    "content": "base64_encoded_data",
    "foreign_content": true,  // SECURITY CRITICAL
    "url": "https://external-site.com/image.png"
}
```

**Security Protocol:**
- `foreign_content: false` - Content is trusted, render faithfully without heavy sanitization
- `foreign_content: true` - Content from external/untrusted sources, apply appropriate security measures:
  - Sanitize content before rendering
  - Consider sandboxing
  - Validate URLs before fetching
  - Apply content security policies

### Event Flow Patterns

#### Typical Interaction Flow
1. Client sends `text_input` (Control Event)
2. Server responds with `interaction` event (`started: true`)
3. Server sends `completion` event (`running: true`)
4. Server streams `text_delta` events with content
5. Server sends `completion` event (`running: false`) with token counts
6. Server sends `interaction` event (`started: false`)
7. Server sends `history_delta` with final messages

#### Session Hierarchy Example
```javascript
// Parent session event
{
    "type": "text_delta",
    "session_id": "sess_parent_123",
    "user_session_id": "sess_parent_123",
    "parent_session_id": null,
    "role": "user",
    "content": "Can you help me with math?"
}

// Child session event (agent delegates to specialized math agent)
{
    "type": "text_delta",
    "session_id": "sess_child_456",
    "user_session_id": "sess_parent_123",
    "parent_session_id": "sess_parent_123",
    "role": "assistant",
    "content": "Let me calculate that for you..."
}
```

## Tool Events

The Agent C Realtime API provides tool event types that enable agents to execute external tools and communicate tool usage to clients. These events are session events that maintain full session correlation and use vendor-specific formats for maximum compatibility with different LLM providers.

### Tool Event Architecture

Tool events inherit from `SessionEvent`, providing complete session context for multi-user environments:

```typescript
interface ToolEvent extends SessionEvent {
  type: string;
  session_id: string;           // Current session identifier
  role: string;                 // Role that triggered the event
  parent_session_id?: string;   // Parent session (for subsessions)
  user_session_id?: string;     // Root user session
  vendor: string;               // LLM provider format indicator
  // ... tool-specific fields
}
```

**Key Architecture Points:**

- **Session Events**: Tool events include full session correlation fields for proper routing
- **Vendor Format**: All tool calls and results use vendor-specific formats (not generic formats)
- **Format Indicator**: The `vendor` field specifies which LLM provider format is used
- **Subsession Support**: Tool events can occur within subsessions and maintain proper hierarchy

### ToolCallEvent

Sent when tool calls are initiated or completed during agent interactions.

**Event Type**: `tool_call`

**Payload**:

```json
{
  "type": "tool_call",
  "session_id": "sess_abc123",
  "role": "assistant", 
  "parent_session_id": null,
  "user_session_id": "sess_abc123",
  "active": true,
  "vendor": "anthropic",
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2",
      "name": "web_search",
      "input": {
        "query": "Python async best practices 2024"
      }
    }
  ],
  "tool_results": [
    {
      "type": "tool_result", 
      "tool_use_id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2",
      "content": [
        {
          "type": "text",
          "text": "Found 15 results for Python async best practices..."
        }
      ]
    }
  ]
}
```

**Fields**:

- **`active`** (boolean): If `true`, tools will be executed immediately after the event is sent
- **`vendor`** (string): LLM provider format indicator
  - `"anthropic"` - Uses Anthropic tool call format with `tool_use` and `tool_result` structures
  - `"openai"` - Uses OpenAI tool call format with `function` calls and responses
- **`tool_calls`** (Array<dict>): Tool calls in vendor-specific format
  - **CRITICAL**: Always in vendor format, never generic format
  - Anthropic format: Uses `type: "tool_use"` with `id`, `name`, and `input` fields
  - OpenAI format: Uses `type: "function"` with `id` and `function` object
- **`tool_results`** (Array<dict>, optional): Tool execution results in vendor format
  - Only present when tools have completed execution
  - Anthropic format: Uses `type: "tool_result"` with `tool_use_id` and `content`
  - OpenAI format: Uses function call response structure

**Vendor Format Examples**:

**Anthropic Tool Format:**
```json
{
  "vendor": "anthropic",
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2",
      "name": "calculate",
      "input": {
        "expression": "2 + 2 * 3"
      }
    }
  ],
  "tool_results": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2", 
      "content": [
        {
          "type": "text",
          "text": "8"
        }
      ]
    }
  ]
}
```

**OpenAI Tool Format:**
```json
{
  "vendor": "openai", 
  "tool_calls": [
    {
      "id": "call_abc123def456",
      "type": "function",
      "function": {
        "name": "calculate",
        "arguments": "{\"expression\": \"2 + 2 * 3\"}"
      }
    }
  ],
  "tool_results": [
    {
      "tool_call_id": "call_abc123def456",
      "role": "tool",
      "name": "calculate", 
      "content": "8"
    }
  ]
}
```

### ToolSelectDeltaEvent  

Sent during streaming when tool calls are being assembled. This event shows tools being selected and constructed in real-time during LLM completion.

**Event Type**: `tool_select_delta`

**Payload**:

```json
{
  "type": "tool_select_delta",
  "session_id": "sess_abc123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_abc123", 
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_01A2B3C4D5E6F7G8H9I0J1K2",
      "name": "web_search",
      "input": {
        "query": "Python async"
      }
    }
  ]
}
```

**Fields**:

- **`tool_calls`** (Array<dict>): Current state of tool calls being assembled
  - Shows partial tool calls during streaming completion
  - Format matches the `vendor` format used in the session
  - Tool calls may be incomplete while streaming (e.g., partial arguments)

**Usage Pattern**:
1. Agent starts completion and begins selecting tools
2. Multiple `tool_select_delta` events show the tool call being built incrementally
3. Final `tool_call` event shows the complete tool calls ready for execution

**Streaming Example Sequence**:

```json
// 1. Initial tool selection
{
  "type": "tool_select_delta",
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_123",
      "name": "web_search"
    }
  ]
}

// 2. Arguments being built
{
  "type": "tool_select_delta", 
  "tool_calls": [
    {
      "type": "tool_use",
      "id": "toolu_123",
      "name": "web_search",
      "input": {
        "query": "Python"
      }
    }
  ]
}

// 3. Final tool selection complete
{
  "type": "tool_call",
  "active": true,
  "tool_calls": [
    {
      "type": "tool_use", 
      "id": "toolu_123",
      "name": "web_search",
      "input": {
        "query": "Python async best practices"
      }
    }
  ]
}
```

### Tool Event Integration

#### Handling Tool Events in Client Code

```javascript
class ToolAwareClient extends AgentCRealtimeClient {
  constructor(jwtToken, baseUrl) {
    super(jwtToken, baseUrl);
    this.setupToolEventHandlers();
    this.activeTool = null;
    this.toolCallBuffer = null;
  }
  
  setupToolEventHandlers() {
    // Handle tool call execution
    this.on('tool_call', (event) => {
      this.handleToolCall(event);
    });
    
    // Handle streaming tool selection
    this.on('tool_select_delta', (event) => {
      this.handleToolSelectDelta(event);
    });
  }
  
  handleToolCall(event) {
    console.log('Tool call event:', {
      active: event.active,
      vendor: event.vendor,
      toolCount: event.tool_calls?.length || 0,
      hasResults: !!event.tool_results,
      sessionContext: {
        sessionId: event.session_id,
        isSubsession: !!event.parent_session_id
      }
    });
    
    // Process based on vendor format
    if (event.vendor === 'anthropic') {
      this.handleAnthropicToolCall(event);
    } else if (event.vendor === 'openai') {
      this.handleOpenAIToolCall(event);
    }
    
    // Update UI to show tool execution
    if (event.active) {
      this.onToolExecutionStarted(event.tool_calls);
    }
    
    if (event.tool_results) {
      this.onToolExecutionCompleted(event.tool_results);
    }
  }
  
  handleAnthropicToolCall(event) {
    event.tool_calls?.forEach(toolCall => {
      if (toolCall.type === 'tool_use') {
        this.displayToolCall({
          id: toolCall.id,
          name: toolCall.name,
          arguments: toolCall.input,
          vendor: 'anthropic'
        });
      }
    });
    
    event.tool_results?.forEach(result => {
      if (result.type === 'tool_result') {
        this.displayToolResult({
          toolId: result.tool_use_id,
          content: result.content,
          vendor: 'anthropic'
        });
      }
    });
  }
  
  handleOpenAIToolCall(event) {
    event.tool_calls?.forEach(toolCall => {
      if (toolCall.type === 'function') {
        this.displayToolCall({
          id: toolCall.id,
          name: toolCall.function.name,
          arguments: JSON.parse(toolCall.function.arguments || '{}'),
          vendor: 'openai'
        });
      }
    });
    
    event.tool_results?.forEach(result => {
      this.displayToolResult({
        toolId: result.tool_call_id,
        name: result.name,
        content: result.content,
        vendor: 'openai'
      });
    });
  }
  
  handleToolSelectDelta(event) {
    console.log('Tool selection streaming:', {
      toolCount: event.tool_calls?.length || 0,
      sessionContext: {
        sessionId: event.session_id,
        isSubsession: !!event.parent_session_id  
      }
    });
    
    // Update tool call buffer with latest state
    this.toolCallBuffer = event.tool_calls;
    
    // Show streaming tool selection in UI
    this.updateToolSelectionUI(event.tool_calls);
  }
  
  displayToolCall(toolInfo) {
    console.log(`🔧 Tool Call (${toolInfo.vendor}):`, {
      id: toolInfo.id,
      name: toolInfo.name,
      arguments: toolInfo.arguments
    });
    
    // Update UI to show tool being called
    this.addToolCallToUI(toolInfo);
  }
  
  displayToolResult(resultInfo) {
    console.log(`✅ Tool Result (${resultInfo.vendor}):`, {
      toolId: resultInfo.toolId,
      content: resultInfo.content
    });
    
    // Update UI to show tool results
    this.addToolResultToUI(resultInfo);
  }
  
  updateToolSelectionUI(toolCalls) {
    // Show that tools are being selected (streaming)
    const toolSelectionElement = document.getElementById('tool-selection');
    if (toolSelectionElement && toolCalls) {
      toolSelectionElement.innerHTML = toolCalls.map(tool => 
        `<div class="selecting-tool">Selecting: ${tool.name || 'unknown'}</div>`
      ).join('');
    }
  }
  
  addToolCallToUI(toolInfo) {
    const chatContainer = document.getElementById('chat-container');
    const toolElement = document.createElement('div');
    toolElement.className = `tool-call ${toolInfo.vendor}`;
    toolElement.innerHTML = `
      <div class="tool-header">
        🔧 <strong>${toolInfo.name}</strong>
        <span class="tool-id">${toolInfo.id}</span>
        <span class="vendor-badge">${toolInfo.vendor}</span>
      </div>
      <div class="tool-arguments">
        <pre>${JSON.stringify(toolInfo.arguments, null, 2)}</pre>
      </div>
    `;
    chatContainer?.appendChild(toolElement);
  }
  
  addToolResultToUI(resultInfo) {
    const toolElement = document.querySelector(`[data-tool-id="${resultInfo.toolId}"]`);
    if (toolElement) {
      const resultElement = document.createElement('div');
      resultElement.className = 'tool-result';
      
      if (resultInfo.vendor === 'anthropic' && Array.isArray(resultInfo.content)) {
        // Anthropic format: content is array of blocks
        resultElement.innerHTML = resultInfo.content.map(block => {
          if (block.type === 'text') {
            return `<div class="text-content">${block.text}</div>`;
          }
          return `<div class="unknown-content">${JSON.stringify(block)}</div>`;
        }).join('');
      } else {
        // OpenAI format or simple text
        resultElement.innerHTML = `<div class="text-content">${resultInfo.content}</div>`;
      }
      
      toolElement.appendChild(resultElement);
    }
  }
}
```

#### Vendor-Specific Processing

```javascript
class VendorAwareToolProcessor {
  static extractToolCalls(toolCallEvent) {
    const { vendor, tool_calls } = toolCallEvent;
    
    if (vendor === 'anthropic') {
      return tool_calls?.filter(call => call.type === 'tool_use').map(call => ({
        id: call.id,
        name: call.name,
        arguments: call.input,
        vendor: 'anthropic'
      })) || [];
    } else if (vendor === 'openai') {
      return tool_calls?.filter(call => call.type === 'function').map(call => ({
        id: call.id,
        name: call.function.name,
        arguments: JSON.parse(call.function.arguments || '{}'),
        vendor: 'openai'
      })) || [];
    }
    
    return [];
  }
  
  static extractToolResults(toolCallEvent) {
    const { vendor, tool_results } = toolCallEvent;
    
    if (!tool_results) return [];
    
    if (vendor === 'anthropic') {
      return tool_results.filter(result => result.type === 'tool_result').map(result => ({
        toolId: result.tool_use_id,
        content: result.content,
        vendor: 'anthropic'
      }));
    } else if (vendor === 'openai') {
      return tool_results.map(result => ({
        toolId: result.tool_call_id,
        name: result.name,
        content: result.content,
        vendor: 'openai'
      }));
    }
    
    return [];
  }
}
```

### Tool Events in Subsessions

Tool events can occur within subsessions and maintain proper session hierarchy:

```json
// Parent session starts subsession
{
  "type": "subsession_started",
  "session_id": "sess_parent_123",
  "sub_agent_type": "tool",
  "sub_agent_key": "web_searcher"
}

// Tool agent selects tools within subsession
{
  "type": "tool_select_delta",
  "session_id": "sess_sub_456",
  "parent_session_id": "sess_parent_123", 
  "user_session_id": "sess_parent_123",
  "role": "assistant",
  "tool_calls": [
    {
      "type": "tool_use",
      "name": "web_search",
      "input": {"query": "weather"}
    }
  ]
}

// Tool execution within subsession
{
  "type": "tool_call",
  "session_id": "sess_sub_456",
  "parent_session_id": "sess_parent_123",
  "user_session_id": "sess_parent_123", 
  "role": "assistant",
  "active": true,
  "vendor": "anthropic",
  "tool_calls": [...],
  "tool_results": [...]
}
```

### Best Practices for Tool Events

1. **Always Check Vendor Format**: Use the `vendor` field to determine tool call structure
2. **Handle Streaming Selection**: Process `tool_select_delta` events for real-time tool selection feedback
3. **Session Awareness**: Use session correlation fields for proper event routing in multi-user environments
4. **Subsession Support**: Handle tool events within subsessions using the session hierarchy
5. **Error Handling**: Implement proper error handling for incomplete or malformed tool calls
6. **UI Differentiation**: Clearly distinguish tool calls from regular conversation in the interface
7. **Security Considerations**: Validate tool results before displaying to users
8. **Performance**: Buffer tool selection deltas appropriately to avoid overwhelming the UI

Tool events enable powerful agent-tool integration while maintaining compatibility with different LLM providers through vendor-specific formats. Proper implementation ensures clients can support the full range of agent capabilities across different backend providers.

## Subsessions: Agent-to-Agent Communication

Subsessions are a fundamental feature of the Agent C Realtime API that enable agent-to-agent communication within the context of a user's chat session. When agents need to collaborate with other agents or delegate work to specialized assistants, these interactions occur in subsessions that are nested within the user's primary session.

### Core Concept

**What are Subsessions?**

Subsessions are nested chat sessions where agents communicate with other agents or specialized tools. These conversations are separate from the user's direct interaction but occur as part of fulfilling the user's request.

**Why Subsessions Exist:**

- **Agent Collaboration**: Enable complex workflows where multiple specialized agents work together
- **Task Delegation**: Allow primary agents to delegate specific tasks to specialized assistants
- **Transparency**: Give users visibility into multi-agent processes while maintaining clear context
- **Scalability**: Support complex, multi-step workflows that involve various AI capabilities

**Key Properties:**

- Subsessions are **nested** within user sessions but have their own session identifiers
- All subsession events are **routed to the user's session** for complete transparency
- Events maintain **correlation metadata** to track the session hierarchy
- Clients receive **the same event types** (text_delta, completion, etc.) but with subsession context

### Session Hierarchy and Event Correlation

The subsession system uses a three-tier session identification system to maintain proper event correlation:

#### Session ID Fields

Every session event includes these correlation fields:

```typescript
interface SessionEvent {
  type: string;
  session_id: string;           // Current session (subsession ID if in subsession)
  role: string;                 // Role that triggered the event
  parent_session_id?: string;   // Parent session ID (if this is a subsession)
  user_session_id?: string;     // Root user session ID (for multi-level nesting)
  // ... event-specific fields
}
```

#### Field Meanings

- **`session_id`**: The immediate session where the event occurred
  - For user sessions: equals the user's chat session ID
  - For subsessions: equals the subsession's unique identifier

- **`parent_session_id`**: The session that spawned this session
  - `null` for root user sessions
  - Set to parent session ID for direct child sessions
  - Set to immediate parent for deeply nested sessions

- **`user_session_id`**: The root user session for the entire interaction tree
  - Always points to the top-level user chat session
  - Allows clients to correlate all related events across any nesting level
  - Critical for multi-user environments

#### Session Hierarchy Examples

**Basic Subsession (2 levels):**

```
User Session (sess_user_123)
└── Agent Subsession (sess_sub_456)
```

Events from the subsession would have:
```json
{
  "session_id": "sess_sub_456",
  "parent_session_id": "sess_user_123", 
  "user_session_id": "sess_user_123"
}
```

**Deep Nesting (4 levels):**

```
User Session (sess_user_123)
└── Primary Agent (sess_agent_456)
    └── Team Member (sess_team_789)
        └── Clone Assistant (sess_clone_999)
```

Events from the clone would have:
```json
{
  "session_id": "sess_clone_999",
  "parent_session_id": "sess_team_789",
  "user_session_id": "sess_user_123"
}
```

### Subsession Lifecycle Events

Subsessions have explicit start and end events that provide context for client UI management.

#### SubsessionStartedEvent

Signals the beginning of a new subsession with metadata for proper client handling.

**Event Type**: `subsession_started`

**Payload**:

```json
{
  "type": "subsession_started",
  "session_id": "sess_parent_123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_parent_123",
  "sub_session_type": "chat",
  "sub_agent_type": "clone", 
  "prime_agent_key": "helpful_assistant",
  "sub_agent_key": "math_expert"
}
```

**Fields**:

- **`sub_session_type`** (string): Category of subsession for styling purposes
  - `"chat"` - Interactive conversation-style subsession
  - `"oneshot"` - Single request/response interaction

- **`sub_agent_type`** (string): Type of agent being used in the subsession
  - `"clone"` - Copy of an existing agent for parallel processing or specialized tasks
  - `"team"` - Team member agent with specific capabilities
  - `"assist"` - Assistant agent for supporting functionality
  - `"tool"` - Agent specifically for tool interaction and execution

- **`prime_agent_key`** (string): The agent key that initiated the subsession

- **`sub_agent_key`** (string): The agent key for the subsession agent

**Usage**: Clients should use this event to:
1. Update UI to show subsession is active
2. Apply appropriate visual styling based on `sub_session_type`
3. Track the agent hierarchy for display purposes

#### SubsessionEndedEvent

Signals the completion of a subsession and return to parent session context.

**Event Type**: `subsession_ended`

**Payload**:

```json
{
  "type": "subsession_ended",
  "session_id": "sess_parent_123",
  "role": "assistant",
  "parent_session_id": null,
  "user_session_id": "sess_parent_123"
}
```

**Usage**: Clients should use this event to:
1. Remove subsession visual indicators
2. Return to parent session styling
3. Update agent hierarchy displays

### Nesting Behavior and Patterns

Subsessions can be nested to arbitrary depths, enabling complex multi-agent workflows.

#### Common Nesting Patterns

**Pattern 1: Direct Delegation**
```
User → Primary Agent → Team Member
```
User asks a complex question, primary agent recognizes it needs specialized help, and creates a subsession with a team member agent.

**Pattern 2: Team Collaboration**
```
User → Team Lead → Team Member 1
                 → Team Member 2  
                 → Team Member 3
```
A team lead agent coordinates multiple team members working on different aspects of a problem.

**Pattern 3: Hierarchical Problem Solving**
```
User → Team Lead → Team Member → Tool Agent
                → Assist Agent → Tool Agent
```
Complex problems broken down into team responsibilities, with each member potentially using tool agents for specific functions.

**Pattern 4: Clone Parallelization**
```
User → Manager → Clone 1
               → Clone 2
               → Clone 3
```
Manager agent creates multiple clones to process tasks in parallel.

#### Nesting Depth Considerations

- **No Hard Limits**: The system supports arbitrary nesting depths
- **Performance Impact**: Deeper nesting increases event volume and complexity
- **User Experience**: Consider visual complexity when displaying deeply nested interactions
- **Common Depths**: Most real-world scenarios use 2-4 levels of nesting

### Event Flow During Subsessions

When a subsession occurs, clients receive a mixed stream of events from both the parent session and the subsession(s). Understanding this flow is critical for proper client implementation.

#### Complete Subsession Flow Example

Here's a complete event sequence showing a user interacting with an agent that delegates to a math specialist:

```json
// 1. User sends message, agent starts processing
{
  "type": "interaction",
  "session_id": "sess_user_123",
  "parent_session_id": null,
  "user_session_id": "sess_user_123", 
  "role": "user",
  "started": true
}

// 2. Agent realizes it needs specialized help
{
  "type": "text_delta",
  "session_id": "sess_user_123",
  "parent_session_id": null,
  "user_session_id": "sess_user_123",
  "role": "assistant", 
  "content": "Let me consult with a specialized team member for this calculation."
}

// 3. Subsession starts
{
  "type": "subsession_started",
  "session_id": "sess_user_123",
  "parent_session_id": null,
  "user_session_id": "sess_user_123",
  "role": "assistant",
  "sub_session_type": "chat",
  "sub_agent_type": "team",
  "prime_agent_key": "helpful_assistant",
  "sub_agent_key": "math_expert"
}

// 4. Team member starts working (different session_id!)
{
  "type": "interaction", 
  "session_id": "sess_sub_456",
  "parent_session_id": "sess_user_123",
  "user_session_id": "sess_user_123",
  "role": "assistant",
  "started": true
}

// 5. Team member provides solution
{
  "type": "text_delta",
  "session_id": "sess_sub_456", 
  "parent_session_id": "sess_user_123",
  "user_session_id": "sess_user_123",
  "role": "assistant",
  "content": "The solution to the integral is: ∫x²dx = x³/3 + C"
}

// 6. Team member completes
{
  "type": "completion",
  "session_id": "sess_sub_456",
  "parent_session_id": "sess_user_123", 
  "user_session_id": "sess_user_123",
  "role": "assistant",
  "running": false,
  "input_tokens": 50,
  "output_tokens": 25
}

// 7. Subsession ends
{
  "type": "subsession_ended",
  "session_id": "sess_user_123",
  "parent_session_id": null,
  "user_session_id": "sess_user_123", 
  "role": "assistant"
}

// 8. Primary agent incorporates results
{
  "type": "text_delta",
  "session_id": "sess_user_123",
  "parent_session_id": null,
  "user_session_id": "sess_user_123",
  "role": "assistant",
  "content": "Based on the team member's calculation, the answer is x³/3 + C. This represents..."
}

// 9. Primary agent completes response
{
  "type": "interaction",
  "session_id": "sess_user_123", 
  "parent_session_id": null,
  "user_session_id": "sess_user_123",
  "role": "user",
  "started": false
}
```

#### Key Flow Characteristics

- **Mixed Event Stream**: Events from parent and child sessions are interleaved
- **Session ID Switching**: The `session_id` changes when entering/exiting subsessions
- **Consistent Correlation**: `parent_session_id` and `user_session_id` provide consistent tracking
- **All Events Routed**: User receives all events from all nested sessions
- **Standard Event Types**: Subsessions use the same event types as regular sessions

### Client Implementation Guide

Implementing subsession support requires careful event handling and UI management.

#### Essential Event Handling

**1. Track Session Hierarchy**

```javascript
class SubsessionTracker {
  constructor() {
    this.sessionStack = [];
    this.currentSession = null;
  }
  
  handleSubsessionStarted(event) {
    // Push current context onto stack
    this.sessionStack.push({
      sessionId: this.currentSession?.sessionId || event.session_id,
      agentKey: this.currentSession?.agentKey || event.prime_agent_key,
      type: this.currentSession?.type || 'user_session'
    });
    
    // Set new subsession as current
    this.currentSession = {
      sessionId: event.session_id, // Note: subsession events will have different session_id
      agentKey: event.sub_agent_key,
      type: event.sub_session_type,
      agentType: event.sub_agent_type
    };
    
    this.onSessionChange(this.currentSession, 'subsession_started');
  }
  
  handleSubsessionEnded(event) {
    // Pop previous context from stack
    const parentContext = this.sessionStack.pop();
    this.currentSession = parentContext;
    
    this.onSessionChange(this.currentSession, 'subsession_ended');
  }
  
  handleSessionEvent(event) {
    // Determine which session this event belongs to
    const sessionInfo = {
      sessionId: event.session_id,
      isSubsession: !!event.parent_session_id,
      parentSessionId: event.parent_session_id,
      userSessionId: event.user_session_id,
      nestingLevel: this.calculateNestingLevel(event)
    };
    
    this.routeEventToUI(event, sessionInfo);
  }
  
  calculateNestingLevel(event) {
    // Count nesting based on session stack depth
    return this.sessionStack.length + (event.parent_session_id ? 1 : 0);
  }
}
```

**2. Event Routing and Display**

```javascript
class SubsessionUIManager {
  constructor() {
    this.messageContainers = new Map(); // Map session_id to UI container
    this.nestingLevel = 0;
  }
  
  routeEventToUI(event, sessionInfo) {
    const container = this.getOrCreateContainer(sessionInfo);
    
    switch (event.type) {
      case 'text_delta':
        this.handleTextDelta(event, container, sessionInfo);
        break;
      case 'interaction':
        this.handleInteraction(event, container, sessionInfo);
        break;
      case 'completion':
        this.handleCompletion(event, container, sessionInfo);
        break;
      // Handle other event types...
    }
  }
  
  getOrCreateContainer(sessionInfo) {
    if (!this.messageContainers.has(sessionInfo.sessionId)) {
      const container = this.createSessionContainer(sessionInfo);
      this.messageContainers.set(sessionInfo.sessionId, container);
    }
    return this.messageContainers.get(sessionInfo.sessionId);
  }
  
  createSessionContainer(sessionInfo) {
    const container = document.createElement('div');
    container.className = `session-container level-${sessionInfo.nestingLevel}`;
    
    if (sessionInfo.isSubsession) {
      container.classList.add('subsession');
      container.classList.add(`subsession-${sessionInfo.type}`);
    }
    
    // Add to parent container
    const parentContainer = sessionInfo.parentSessionId 
      ? this.messageContainers.get(sessionInfo.parentSessionId)
      : document.getElementById('main-chat');
      
    parentContainer.appendChild(container);
    return container;
  }
  
  handleTextDelta(event, container, sessionInfo) {
    // Apply visual differentiation based on nesting
    const message = document.createElement('div');
    message.className = `message role-${event.role} level-${sessionInfo.nestingLevel}`;
    
    if (sessionInfo.isSubsession) {
      message.classList.add('subsession-message');
    }
    
    message.textContent = event.content;
    container.appendChild(message);
  }
}
```

#### Visual Differentiation Requirements

Clients **must** provide visual differentiation for subsession content to avoid user confusion.

**Required Visual Elements:**

1. **Indentation/Nesting**: Subsessions should be visually indented or contained
2. **Color Coding**: Different background colors or borders for different session types
3. **Agent Attribution**: Clear indication of which agent is speaking
4. **Nesting Level Indicators**: Visual cues for the depth of nesting
5. **Session Boundaries**: Clear start/end markers for subsessions

**Recommended CSS Structure:**

```css
.session-container {
  border-left: 3px solid #e0e0e0;
  margin-left: 10px;
  padding-left: 15px;
}

.session-container.subsession {
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 8px 0;
  padding: 12px;
}

.session-container.level-1 { margin-left: 0px; }
.session-container.level-2 { margin-left: 20px; }
.session-container.level-3 { margin-left: 40px; }
.session-container.level-4 { margin-left: 60px; }

.session-container.subsession-chat {
  border-left-color: #007bff;
}

.session-container.subsession-oneshot {
  border-left-color: #28a745;
}

.message.subsession-message {
  font-style: italic;
  opacity: 0.9;
}

.agent-badge {
  display: inline-block;
  background: #6c757d;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  margin-right: 8px;
}
```

#### React Implementation Example

```jsx
const SubsessionChat = () => {
  const [sessionHierarchy, setSessionHierarchy] = useState([]);
  const [messages, setMessages] = useState(new Map());

  const handleEvent = useCallback((event) => {
    switch (event.type) {
      case 'subsession_started':
        setSessionHierarchy(prev => [...prev, {
          sessionId: event.session_id,
          type: event.sub_session_type,
          agentType: event.sub_agent_type,
          agentKey: event.sub_agent_key,
          level: prev.length
        }]);
        break;
        
      case 'subsession_ended':
        setSessionHierarchy(prev => prev.slice(0, -1));
        break;
        
      case 'text_delta':
        const sessionInfo = {
          sessionId: event.session_id,
          isSubsession: !!event.parent_session_id,
          level: calculateLevel(event, sessionHierarchy)
        };
        
        setMessages(prev => {
          const newMessages = new Map(prev);
          const sessionMessages = newMessages.get(event.session_id) || [];
          sessionMessages.push({ ...event, sessionInfo });
          newMessages.set(event.session_id, sessionMessages);
          return newMessages;
        });
        break;
    }
  }, [sessionHierarchy]);

  const renderMessage = (message) => (
    <div 
      key={message.id}
      className={`
        message 
        level-${message.sessionInfo.level}
        ${message.sessionInfo.isSubsession ? 'subsession-message' : ''}
      `}
      style={{
        marginLeft: `${message.sessionInfo.level * 20}px`,
        backgroundColor: message.sessionInfo.isSubsession ? '#f8f9fa' : 'white',
        borderLeft: message.sessionInfo.isSubsession ? '3px solid #007bff' : 'none'
      }}
    >
      {message.sessionInfo.isSubsession && (
        <span className="agent-badge">
          {getAgentName(message.sessionInfo.agentKey)}
        </span>
      )}
      {message.content}
    </div>
  );

  return (
    <div className="chat-container">
      {Array.from(messages.values()).flat().map(renderMessage)}
    </div>
  );
};
```

### Advanced Scenarios

#### Concurrent Subsessions

Some agents may spawn multiple subsessions simultaneously:

```json
// Agent starts multiple team members
{
  "type": "subsession_started",
  "sub_session_type": "chat", 
  "sub_agent_type": "team",
  "sub_agent_key": "math_expert"
}

{
  "type": "subsession_started", 
  "sub_session_type": "chat",
  "sub_agent_type": "team",
  "sub_agent_key": "physics_expert"  
}

// Events from both subsessions interleave
{
  "type": "text_delta",
  "session_id": "sess_math_456",
  "content": "Calculating integral..."
}

{
  "type": "text_delta", 
  "session_id": "sess_physics_789",
  "content": "Analyzing quantum mechanics..."
}
```

**Client Handling**: Track multiple active subsessions and render them in parallel containers.

#### Error Handling in Subsessions

```json
// Subsession encounters an error
{
  "type": "error",
  "session_id": "sess_sub_456",
  "parent_session_id": "sess_user_123",
  "user_session_id": "sess_user_123",
  "message": "Team member encountered an error"
}

// Parent agent handles the error
{
  "type": "text_delta",
  "session_id": "sess_user_123", 
  "content": "I'll try a different approach to solve this problem."
}
```

**Client Handling**: Display subsession errors in context but ensure parent session can continue.

### Debugging and Troubleshooting

#### Common Issues

1. **Lost Session Context**: Events not properly correlated to sessions
   - **Solution**: Always check `parent_session_id` and `user_session_id` fields
   - **Debug**: Log session hierarchy state on each event

2. **Visual Confusion**: User can't distinguish subsession content
   - **Solution**: Implement proper visual differentiation
   - **Debug**: Ensure CSS classes are applied correctly

3. **Memory Leaks**: Session containers not cleaned up
   - **Solution**: Remove containers when sessions end
   - **Debug**: Monitor DOM node count during long conversations

4. **Event Ordering Issues**: Events arrive out of order
   - **Solution**: Buffer events by session_id and process in sequence
   - **Debug**: Log event timestamps and session IDs

#### Debug Mode Implementation

```javascript
class SubsessionDebugger {
  constructor() {
    this.eventLog = [];
    this.sessionTree = {};
  }
  
  logEvent(event) {
    this.eventLog.push({
      timestamp: Date.now(),
      event: event,
      sessionTree: JSON.stringify(this.sessionTree, null, 2)
    });
    
    if (this.eventLog.length > 1000) {
      this.eventLog = this.eventLog.slice(-500); // Keep recent events
    }
    
    console.log('🔍 Subsession Debug:', {
      type: event.type,
      sessionId: event.session_id,
      parentId: event.parent_session_id,
      userSessionId: event.user_session_id,
      currentTree: this.sessionTree
    });
  }
  
  exportDebugLog() {
    return {
      eventLog: this.eventLog,
      sessionTree: this.sessionTree,
      timestamp: new Date().toISOString()
    };
  }
}
```

### Best Practices

1. **Always Track Session Hierarchy**: Maintain a clear understanding of the current session context
2. **Visual Differentiation is Required**: Users must be able to distinguish subsession content
3. **Handle Concurrent Subsessions**: Be prepared for multiple simultaneous subsessions  
4. **Graceful Error Handling**: Subsession errors shouldn't break the parent session
5. **Performance Monitoring**: Deep nesting can impact performance - monitor and optimize
6. **Accessibility**: Ensure screen readers can navigate the session hierarchy
7. **Mobile Considerations**: Adapt visual differentiation for smaller screens
8. **Testing**: Include subsession scenarios in your integration testing

Subsessions enable powerful multi-agent workflows while maintaining transparency for users. Proper implementation ensures users can understand and follow complex agent collaborations seamlessly.

## Chat Sessions

The Agent C Realtime API maintains chat sessions that store conversation history in vendor-specific message formats. Understanding the chat session structure is crucial for proper client integration, especially when handling message history and vendor differences.

### ChatSession Model

The `ChatSession` model represents a complete conversation session with the following key structure:

```typescript
interface ChatSession {
  version: number;                    // Schema version (currently 1)
  session_id: string;                // Unique session identifier  
  token_count: number;               // Total tokens used in session
  context_window_size: number;       // Context window size in tokens
  session_name?: string;             // Optional display name
  created_at?: string;               // ISO timestamp
  updated_at?: string;               // ISO timestamp
  deleted_at?: string;               // ISO timestamp (if soft-deleted)
  user_id?: string;                  // User identifier (defaults to "admin")
  metadata?: Record<string, any>;    // Additional session metadata
  messages: Array<Record<string, any>>; // Vendor-specific message array
  agent_config?: AgentConfiguration; // Agent configuration
  
  // Computed properties
  vendor: string;                    // "anthropic" | "openai" | "none"
  display_name: string;              // Computed display name
}
```

#### Vendor Field

The `vendor` field is a computed property that determines the format of messages in the session:

- **"anthropic"**: Messages follow the Anthropic SDK MessageParam format
- **"openai"**: Messages follow the OpenAI API message format  
- **"none"**: No agent configured, messages format undefined

The vendor is automatically determined based on the agent's `model_id`:
- Models starting with "claude" or "bedrock" → "anthropic" 
- All other models → "openai"

### Message Formats by Vendor

#### Anthropic Message Format

When `vendor: "anthropic"`, messages follow the Anthropic SDK MessageParam structure:

```typescript
// Basic text message
{
  role: "user" | "assistant",
  content: string | Array<ContentBlockParam>
}

// Message with mixed content
{
  role: "user",
  content: [
    {
      type: "text",
      text: "Please analyze this image:"
    },
    {
      type: "image", 
      source: {
        type: "base64",
        media_type: "image/png",
        data: "iVBORw0KGgoAAAANSUhEUgAA..."
      }
    }
  ]
}

// Tool usage message
{
  role: "assistant",
  content: [
    {
      type: "text",
      text: "I'll search for that information."
    },
    {
      type: "tool_use",
      id: "toolu_123",
      name: "web_search", 
      input: {
        query: "TypeScript best practices 2024"
      }
    }
  ]
}
```

For complete Anthropic MessageParam type definitions, refer to the [Anthropic TypeScript Reference](//realtime_client/.scratch/chat_session_ref/anthropic_message_param_typescript_reference.md).

#### OpenAI Message Format

When `vendor: "openai"`, messages follow the standard OpenAI API format:

```typescript
// Text message
{
  role: "user" | "assistant" | "system",
  content: string
}

// Message with image (GPT-4V)
{
  role: "user",
  content: [
    {
      type: "text",
      text: "What's in this image?"
    },
    {
      type: "image_url",
      image_url: {
        url: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      }
    }
  ]
}

// Tool call message
{
  role: "assistant",
  content: null,
  tool_calls: [
    {
      id: "call_abc123",
      type: "function",
      function: {
        name: "get_weather",
        arguments: "{\"location\": \"New York\"}"
      }
    }
  ]
}
```

### ChatSessionIndexEntry Model

The `ChatSessionIndexEntry` provides a lightweight representation of chat sessions for listing and indexing:

```typescript
interface ChatSessionIndexEntry {
  session_id: string;        // Unique session identifier
  session_name?: string;     // Optional display name
  created_at?: string;       // ISO timestamp
  updated_at?: string;       // ISO timestamp  
  user_id?: string;          // User identifier
  agent_key?: string;        // Agent key used in session
  agent_name?: string;       // Agent display name
}
```

This model is used in session lists and search results to provide essential session information without loading full message history.

### Chat Session Events

#### chat_session_changed Event

Sent when a chat session is created, updated, or when session metadata changes.

**Event Type**: `chat_session_changed`

**Payload**:

```json
{
  "type": "chat_session_changed",
  "session_id": "string",
  "session": {
    "session_id": "string",
    "vendor": "anthropic",
    "session_name": "string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "user_id": "user_123",
    "agent_config": {
      "key": "helpful_assistant",
      "name": "Helpful Assistant",
      "model_id": "claude-3-sonnet-20240229"
    },
    "token_count": 1250,
    "context_window_size": 200000,
    "metadata": {
      "topic": "Python Programming"
    }
  }
}
```

**Fields**:
- `session_id` (string): The session that changed
- `session` (object): Complete session information including:
  - `vendor` (string): Message format ("anthropic", "openai", "none")
  - Standard ChatSession fields (see model above)
  - **Note**: `messages` array is typically omitted for performance

### Working with Vendor-Specific Messages

#### Handling Message History

When processing `history_delta` or `history` events, check the vendor field to handle messages appropriately:

```javascript
class ChatHistoryHandler {
  processHistory(historyEvent) {
    const { vendor, messages } = historyEvent;
    
    messages.forEach(message => {
      if (vendor === 'anthropic') {
        this.handleAnthropicMessage(message);
      } else if (vendor === 'openai') {
        this.handleOpenAIMessage(message);
      }
    });
  }
  
  handleAnthropicMessage(message) {
    // message.content can be string or Array<ContentBlockParam>
    if (typeof message.content === 'string') {
      this.displayText(message.role, message.content);
    } else if (Array.isArray(message.content)) {
      message.content.forEach(block => {
        switch (block.type) {
          case 'text':
            this.displayText(message.role, block.text);
            break;
          case 'image':
            this.displayImage(block.source);
            break;
          case 'tool_use':
            this.displayToolCall(block.name, block.input);
            break;
          // Handle other content types...
        }
      });
    }
  }
  
  handleOpenAIMessage(message) {
    // OpenAI format handling
    if (message.content) {
      if (typeof message.content === 'string') {
        this.displayText(message.role, message.content);
      } else if (Array.isArray(message.content)) {
        // Handle OpenAI content array format
        message.content.forEach(item => {
          if (item.type === 'text') {
            this.displayText(message.role, item.text);
          } else if (item.type === 'image_url') {
            this.displayImageUrl(item.image_url.url);
          }
        });
      }
    }
    
    // Handle tool calls (OpenAI format)
    if (message.tool_calls) {
      message.tool_calls.forEach(toolCall => {
        this.displayToolCall(toolCall.function.name, 
          JSON.parse(toolCall.function.arguments));
      });
    }
  }
}
```

#### Content Extraction Utilities

```javascript
// Extract plain text from vendor-specific message
function extractMessageText(message, vendor) {
  if (vendor === 'anthropic') {
    if (typeof message.content === 'string') {
      return message.content;
    }
    return message.content
      .filter(block => block.type === 'text')
      .map(block => block.text)
      .join('');
  } else if (vendor === 'openai') {
    if (typeof message.content === 'string') {
      return message.content;
    }
    return message.content
      .filter(item => item.type === 'text')
      .map(item => item.text)
      .join('');
  }
  return '';
}

// Check if message contains media content
function hasMediaContent(message, vendor) {
  if (vendor === 'anthropic') {
    return Array.isArray(message.content) && 
           message.content.some(block => 
             ['image', 'document'].includes(block.type));
  } else if (vendor === 'openai') {
    return Array.isArray(message.content) &&
           message.content.some(item => item.type === 'image_url');
  }
  return false;
}
```

### Migration Considerations

#### Handling Legacy Sessions

Sessions created before the vendor field implementation may not have explicit vendor information. In these cases:

1. The `vendor` computed property will return "none" if no agent configuration exists
2. Message format should be inferred from message structure
3. Consider implementing format detection utilities:

```javascript
function detectMessageFormat(message) {
  // Anthropic format indicators
  if (Array.isArray(message.content)) {
    const hasAnthropicBlocks = message.content.some(block => 
      block.type && ['text', 'tool_use', 'image'].includes(block.type));
    if (hasAnthropicBlocks) return 'anthropic';
  }
  
  // OpenAI format indicators  
  if (message.tool_calls) return 'openai';
  if (Array.isArray(message.content) && 
      message.content.some(item => item.type === 'image_url')) {
    return 'openai';
  }
  
  // Default to simple text format
  return 'unknown';
}
```

#### Version Compatibility

The `version` field in ChatSession tracks schema evolution:
- **Version 1**: Current schema with vendor-specific messages
- Future versions will increment as the schema evolves

Always check the version field when processing sessions to ensure compatibility.

### Best Practices

1. **Check Vendor Field**: Always check the `vendor` field before processing messages
2. **Handle Both Formats**: Implement handlers for both Anthropic and OpenAI message formats
3. **Graceful Degradation**: Handle unknown or mixed formats gracefully
4. **Content Type Detection**: Use type fields to properly render different content blocks
5. **Tool Call Handling**: Remember that tool calls are structured differently between vendors
6. **Media Content**: Handle images and documents according to vendor-specific formats
7. **Legacy Support**: Be prepared to handle sessions without explicit vendor information

## Quick Start

### 1. Basic Connection Setup

```javascript
class AgentCRealtimeClient {
    constructor(jwtToken, baseUrl = 'wss://your-api-domain.com') {
        this.token = jwtToken;
        this.wsUrl = `${baseUrl}/api/avatar/ws`;
        this.ws = null;
        this.isConnected = false;
        this.eventHandlers = new Map();
        this.currentInteraction = null;
        this.agents = [];
        this.avatars = [];
    }

    async connect() {
        return new Promise((resolve, reject) => {
            // Include JWT token in connection (implementation varies by platform)
            this.ws = new WebSocket(`${this.wsUrl}?token=${this.token}`);

            this.ws.onopen = () => {
                console.log('Connected to Agent C Realtime API');
                this.isConnected = true;
                resolve();
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

            this.ws.onclose = () => {
                console.log('Disconnected from Agent C Realtime API');
                this.isConnected = false;
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }

    sendEvent(event) {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify(event));
        } else {
            throw new Error('Not connected to API');
        }
    }
}
```

### 2. Event Handling System

```javascript
class AgentCRealtimeClient {
    // ... previous code ...

    handleMessage(event) {
        console.log('Received event:', event.type, event);

        // Call registered handlers
        const handler = this.eventHandlers.get(event.type);
        if (handler) {
            handler(event);
        } else {
            console.warn('No handler for event type:', event.type);
        }
    }

    on(eventType, handler) {
        this.eventHandlers.set(eventType, handler);
    }

    off(eventType) {
        this.eventHandlers.delete(eventType);
    }
}
```

### 3. Session Setup

```javascript
class AgentCRealtimeClient {
    // ... previous code ...

    async setupSession(agentKey, avatarId) {
        // Wait for initial agent and avatar lists
        await this.waitForInitialData();

        // Set the agent
        await this.setAgent(agentKey);

        // Set the avatar
        await this.setAvatar(avatarId);

        console.log('Session setup complete');
    }

    waitForInitialData() {
        return new Promise((resolve) => {
            let receivedAgents = false;
            let receivedAvatars = false;

            const checkComplete = () => {
                if (receivedAgents && receivedAvatars) {
                    resolve();
                }
            };

            this.on('agent_list', (event) => {
                this.agents = event.agents;
                receivedAgents = true;
                checkComplete();
            });

            this.on('avatar_list', (event) => {
                this.avatars = event.avatars;
                receivedAvatars = true;
                checkComplete();
            });
        });
    }

    async setAgent(agentKey) {
        return new Promise((resolve, reject) => {
            // Set up response handler
            const timeout = setTimeout(() => {
                reject(new Error('Agent setup timeout'));
            }, 5000);

            this.on('agent_configuration_changed', (event) => {
                clearTimeout(timeout);
                console.log('Agent set:', event.agent_config);
                resolve(event.agent_config);
            });

            this.on('error', (event) => {
                clearTimeout(timeout);
                reject(new Error(event.message));
            });

            // Send the request
            this.sendEvent({
                type: 'set_agent',
                agent_key: agentKey
            });
        });
    }

    async setAvatar(avatarId, quality = 'medium', videoEncoding = 'VP8') {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Avatar setup timeout'));
            }, 10000); // Avatar setup can take longer

            this.on('avatar_connection_changed', (event) => {
                clearTimeout(timeout);
                console.log('Avatar set:', event.avatar_session);
                resolve(event.avatar_session);
            });

            this.on('error', (event) => {
                clearTimeout(timeout);
                reject(new Error(event.message));
            });

            this.sendEvent({
                type: 'set_avatar',
                avatar_id: avatarId,
                quality: quality,
                video_encoding: videoEncoding
            });
        });
    }
}
```

## Complete Working Example

```javascript
class AgentCChatClient extends AgentCRealtimeClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.setupEventHandlers();
        this.messageBuffer = new Map(); // Buffer messages by role
        this.thoughtBuffer = '';
    }

    setupEventHandlers() {
        // Note: Session events include session_id, role, and optional parent_session_id/user_session_id fields
        // Control events do not include these session context fields
        
        // Interaction management (Session Event)
        this.on('interaction', (event) => {
            // event includes: session_id, role, started, id
            this.currentInteraction = event.started ? event.id : null;
            this.onInteractionStateChange(event.started);
        });

        // Text streaming (Session Event)
        this.on('text_delta', (event) => {
            // event includes: session_id, role, content, format
            this.appendToBuffer(event.role, event.content);
            this.onTextDelta(event);
        });

        // Thought streaming (Session Event)
        this.on('thought_delta', (event) => {
            // event includes: session_id, role (with " (thought)" suffix), content, format
            this.thoughtBuffer += event.content;
            this.onThoughtDelta(event);
        });

        // Completion tracking (Session Event)
        this.on('completion', (event) => {
            // event includes: session_id, role, running, completion_options, stop_reason, input_tokens, output_tokens
            this.onCompletion(event);
        });

        // Error handling (Control Event)
        this.on('error', (event) => {
            // event includes: message, source (no session context)
            this.onError(event);
        });

        // History updates (Session Event)
        this.on('history_delta', (event) => {
            // event includes: session_id, role, vendor, messages
            this.onHistoryUpdate(event);
        });
        
        // Media rendering with security handling (Session Event)
        this.on('render_media', (event) => {
            // event includes: session_id, role, content_type, url, content, foreign_content, etc.
            this.onRenderMedia(event);
        });
        
        // Subsession management (Session Events)
        this.on('subsession_started', (event) => {
            // event includes: session_id, role, sub_session_type, sub_agent_type, prime_agent_key, sub_agent_key
            this.onSubsessionStarted(event);
        });
        
        this.on('subsession_ended', (event) => {
            // event includes: session_id, role
            this.onSubsessionEnded(event);
        });
    }

    appendToBuffer(role, content) {
        if (!this.messageBuffer.has(role)) {
            this.messageBuffer.set(role, '');
        }
        this.messageBuffer.set(role, this.messageBuffer.get(role) + content);
    }

    async sendMessage(text, fileIds = []) {
        if (!this.isConnected) {
            throw new Error('Not connected');
        }

        if (this.currentInteraction) {
            throw new Error('Interaction already in progress');
        }

        // Clear buffers
        this.messageBuffer.clear();
        this.thoughtBuffer = '';

        this.sendEvent({
            type: 'text_input',
            text: text,
            file_ids: fileIds
        });
    }

    // Override these methods in your implementation
    onInteractionStateChange(isActive) {
        console.log('Interaction active:', isActive);
        // Update UI to disable/enable input
    }

    onTextDelta(event) {
        console.log('Text delta:', event.content);
        // Update UI with streaming text
    }

    onThoughtDelta(event) {
        console.log('Thought delta:', event.content);
        // Show thinking process in UI
    }

    onCompletion(event) {
        console.log('Completion:', event);
        // Handle completion (token usage, etc.)
    }

    onError(event) {
        console.error('API Error:', event.message);
        // Show error to user
    }

    onHistoryUpdate(event) {
        console.log('History updated:', event.messages);
        // Update chat history in UI
    }
    
    onRenderMedia(event) {
        console.log('Render media:', event.content_type);
        
        // SECURITY: Handle foreign content appropriately
        if (event.foreign_content) {
            // Content from external/untrusted sources - apply security measures
            console.warn('Foreign content detected - applying security measures');
            this.renderUntrustedMedia(event);
        } else {
            // Trusted content from agent/tools - render faithfully
            this.renderTrustedMedia(event);
        }
    }
    
    renderTrustedMedia(event) {
        // Render internal content faithfully without heavy sanitization
        if (event.content) {
            // Base64 content
            const blob = this.base64ToBlob(event.content, event.content_type);
            this.displayMediaBlob(blob, event.name);
        } else if (event.url) {
            // Trusted URL
            this.displayMediaUrl(event.url, event.name);
        }
    }
    
    renderUntrustedMedia(event) {
        // Apply security measures for foreign content
        if (event.content) {
            // Sanitize and validate base64 content
            const sanitizedContent = this.sanitizeBase64Content(event.content);
            if (sanitizedContent) {
                const blob = this.base64ToBlob(sanitizedContent, event.content_type);
                this.displayMediaBlob(blob, event.name, { sandboxed: true });
            }
        } else if (event.url) {
            // Validate URL and apply CSP
            if (this.validateUrl(event.url)) {
                this.displayMediaUrl(event.url, event.name, { sandboxed: true });
            } else {
                console.warn('Blocked potentially unsafe URL:', event.url);
            }
        }
    }
    
    base64ToBlob(base64, contentType) {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: contentType });
    }
    
    validateUrl(url) {
        try {
            const urlObj = new URL(url);
            // Only allow HTTPS for external URLs
            return urlObj.protocol === 'https:';
        } catch {
            return false;
        }
    }
    
    sanitizeBase64Content(content) {
        // Implement content validation/sanitization as needed
        // This is a placeholder - real implementation depends on content type
        return content; // After validation
    }
    
    displayMediaBlob(blob, name, options = {}) {
        // Implementation for displaying blob content
        console.log('Display blob:', blob.type, name, options);
    }
    
    displayMediaUrl(url, name, options = {}) {
        // Implementation for displaying URL content
        console.log('Display URL:', url, name, options);
    }
    
    onSubsessionStarted(event) {
        console.log('Subsession started:', {
            type: event.sub_session_type,
            agentType: event.sub_agent_type,
            primeAgent: event.prime_agent_key,
            subAgent: event.sub_agent_key,
            sessionId: event.session_id
        });
        
        // Track session hierarchy for proper event routing
        this.sessionStack = this.sessionStack || [];
        this.sessionStack.push(this.currentSubsession || {
            type: 'user_session',
            sessionId: event.session_id,
            agentKey: event.prime_agent_key
        });
        
        // Set new subsession context
        this.currentSubsession = {
            type: event.sub_session_type,
            agentType: event.sub_agent_type,
            primeAgentKey: event.prime_agent_key,
            subAgentKey: event.sub_agent_key,
            sessionId: event.session_id,
            nestingLevel: this.sessionStack.length
        };
        
        // Update UI to show subsession is active
        // Apply visual differentiation based on subsession type
        this.updateSubsessionUI(this.currentSubsession, 'started');
        
        // Events following this will have different session_id values for subsession events
        // Use parent_session_id and user_session_id for correlation
    }
    
    onSubsessionEnded(event) {
        console.log('Subsession ended:', {
            sessionId: event.session_id,
            endedSubsession: this.currentSubsession
        });
        
        // Update UI to indicate subsession has ended
        if (this.currentSubsession) {
            this.updateSubsessionUI(this.currentSubsession, 'ended');
        }
        
        // Pop previous context from session stack
        this.sessionStack = this.sessionStack || [];
        this.currentSubsession = this.sessionStack.pop() || null;
        
        // Events following this will be from the parent session context
        console.log('Returning to parent context:', this.currentSubsession);
    }
    
    updateSubsessionUI(subsessionInfo, action) {
        // Example UI management for subsessions
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;
        
        if (action === 'started') {
            // Add visual indicator for subsession
            const indicator = document.createElement('div');
            indicator.className = `subsession-indicator ${subsessionInfo.type}`;
            indicator.id = `subsession-${subsessionInfo.sessionId}`;
            indicator.innerHTML = `
                <div class="subsession-header">
                    <span class="subsession-type">${subsessionInfo.type.replace('_', ' ')}</span>
                    <span class="subsession-agent">${subsessionInfo.subAgentKey}</span>
                    <span class="nesting-level">Level ${subsessionInfo.nestingLevel}</span>
                </div>
            `;
            chatContainer.appendChild(indicator);
        } else if (action === 'ended') {
            // Remove or update subsession indicator
            const indicator = document.getElementById(`subsession-${subsessionInfo.sessionId}`);
            if (indicator) {
                indicator.classList.add('subsession-ended');
                // Could remove it or keep it for history
                setTimeout(() => indicator.remove(), 3000);
            }
        }
    }
    
    // Enhanced event handler that considers subsession context
    handleSessionEvent(event) {
        // Determine session context for this event
        const sessionContext = {
            sessionId: event.session_id,
            isSubsession: !!event.parent_session_id,
            parentSessionId: event.parent_session_id,
            userSessionId: event.user_session_id,
            nestingLevel: this.calculateNestingLevel(event)
        };
        
        // Route event to appropriate handler with session context
        switch (event.type) {
            case 'text_delta':
                this.onTextDeltaWithContext(event, sessionContext);
                break;
            case 'interaction':
                this.onInteractionWithContext(event, sessionContext);
                break;
            case 'completion':
                this.onCompletionWithContext(event, sessionContext);
                break;
            // Handle other events with session context...
        }
    }
    
    calculateNestingLevel(event) {
        if (!event.parent_session_id) return 0;
        return (this.sessionStack?.length || 0) + 1;
    }
    
    onTextDeltaWithContext(event, sessionContext) {
        // Enhanced text delta handling with subsession awareness
        const messageClass = sessionContext.isSubsession ? 'subsession-message' : 'main-message';
        const indentLevel = sessionContext.nestingLevel * 20; // 20px per level
        
        console.log('Text delta with context:', {
            content: event.content,
            role: event.role,
            sessionContext: sessionContext,
            messageClass: messageClass
        });
        
        // Apply visual differentiation based on subsession context
        this.appendToBuffer(event.role, event.content, {
            sessionContext: sessionContext,
            messageClass: messageClass,
            indentLevel: indentLevel
        });
    }
}
```

## Usage Examples

### Basic Chat Session

```javascript
async function startChatSession() {
    const client = new AgentCChatClient('your-jwt-token');

    try {
        // Connect to API
        await client.connect();

        // Setup session with specific agent and avatar
        await client.setupSession('helpful_assistant', 'anna_public_3_20240108');

        // Send a message
        await client.sendMessage('Hello! Can you help me understand quantum physics?');

        // The response will come through event handlers

    } catch (error) {
        console.error('Session setup failed:', error);
    }
}
```

### Avatar Integration with HeyGen

```javascript
class AvatarChatClient extends AgentCChatClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.heygenSession = null;
        this.avatarWebSocket = null;
    }

    async setAvatar(avatarId, quality, videoEncoding) {
        const avatarSession = await super.setAvatar(avatarId, quality, videoEncoding);
        this.heygenSession = avatarSession;

        // Connect to HeyGen for avatar video/audio
        await this.connectToHeyGenAvatar(avatarSession);

        return avatarSession;
    }

    async connectToHeyGenAvatar(session) {
        // Connect to HeyGen WebSocket for avatar stream
        // Note: HeyGen uses the access token as session_token in the WebSocket URL
        const wsUrl = `wss://${new URL(session.url).hostname}/v1/ws/streaming.chat?session_id=${session.session_id}&session_token=${session.access_token}`;
        this.avatarWebSocket = new WebSocket(wsUrl);

        this.avatarWebSocket.onopen = () => {
            console.log('Connected to HeyGen WebSocket');
            // No additional authentication needed - token is in URL
        };

        this.avatarWebSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleHeyGenEvent(data);
        };
    }

    handleHeyGenEvent(event) {
        switch (event.type) {
            case 'avatar_start_talking':
                this.onAvatarStartTalking();
                break;
            case 'avatar_stop_talking':
                this.onAvatarStopTalking();
                break;
            case 'stream_ready':
                this.onAvatarStreamReady(event.detail);
                break;
        }
    }

    onAvatarStartTalking() {
        console.log('Avatar started talking');
        // Update UI to show avatar is speaking
    }

    onAvatarStopTalking() {
        console.log('Avatar stopped talking');
        // Update UI to show avatar is idle
    }

    onAvatarStreamReady(streamDetail) {
        console.log('Avatar stream ready:', streamDetail);
        // Connect video element to MediaStream (not URL)
        const video = document.getElementById('avatar-video');
        if (streamDetail instanceof MediaStream) {
            video.srcObject = streamDetail;
            video.play();
        }
    }
}
```

### Error Handling and Reconnection

```javascript
class RobustAgentCClient extends AgentCChatClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
    }

    async connect() {
        try {
            await super.connect();
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        } catch (error) {
            console.error('Connection failed:', error);
            await this.handleReconnection();
        }
    }

    async handleReconnection() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.onMaxReconnectAttemptsReached();
            return;
        }

        this.reconnectAttempts++;
        console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, this.reconnectDelay));
        this.reconnectDelay *= 2;

        try {
            await this.connect();
        } catch (error) {
            await this.handleReconnection();
        }
    }

    onMaxReconnectAttemptsReached() {
        // Notify user that connection failed
        console.error('Unable to connect to Agent C API');
    }
}
```

## React Integration Example

```jsx
import React, { useState, useEffect, useCallback } from 'react';

const AgentCChat = ({ jwtToken }) => {
    const [client, setClient] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [isInteracting, setIsInteracting] = useState(false);
    const [thoughts, setThoughts] = useState('');

    useEffect(() => {
        const chatClient = new AgentCChatClient(jwtToken);

        // Override event handlers for React
        chatClient.onInteractionStateChange = setIsInteracting;

        chatClient.onTextDelta = (event) => {
            setCurrentMessage(prev => prev + event.content);
        };

        chatClient.onThoughtDelta = (event) => {
            setThoughts(prev => prev + event.content);
        };

        chatClient.onHistoryUpdate = (event) => {
            setMessages(event.messages);
            setCurrentMessage(''); // Clear current message buffer
            setThoughts(''); // Clear thoughts
        };

        chatClient.connect()
            .then(() => {
                setIsConnected(true);
                return chatClient.setupSession('helpful_assistant', 'anna_public_3_20240108');
            })
            .catch(console.error);

        setClient(chatClient);

        return () => {
            chatClient.disconnect();
        };
    }, [jwtToken]);

    const sendMessage = useCallback(async (text) => {
        if (client && !isInteracting) {
            try {
                await client.sendMessage(text);
            } catch (error) {
                console.error('Failed to send message:', error);
            }
        }
    }, [client, isInteracting]);

    return (
        <div className="agent-c-chat">
            <div className="connection-status">
                Status: {isConnected ? 'Connected' : 'Disconnected'}
            </div>

            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        <strong>{msg.role}:</strong> {msg.content}
                    </div>
                ))}

                {currentMessage && (
                    <div className="message assistant current">
                        <strong>assistant:</strong> {currentMessage}
                    </div>
                )}
            </div>

            {thoughts && (
                <div className="thoughts">
                    <em>Thinking: {thoughts}</em>
                </div>
            )}

            <ChatInput 
                onSendMessage={sendMessage} 
                disabled={!isConnected || isInteracting} 
            />
        </div>
    );
};
```

## Best Practices

### 1. Connection Management

- Implement exponential backoff for reconnections
- Handle network interruptions gracefully
- Validate JWT token expiration and refresh as needed

### 2. Event Handling

- Always implement error event handlers
- Buffer text deltas appropriately for your UI
- Handle unknown event types gracefully

### 3. State Management

- Track interaction state to prevent concurrent requests
- Maintain local message history for better UX
- Clear buffers appropriately between interactions

### 4. Performance

- Debounce rapid UI updates from text deltas
- Use efficient data structures for message buffering
- Implement proper cleanup on component unmount

### 5. User Experience

- Show loading states during interactions
- Display thinking process when available
- Provide clear error messages to users
- Disable input during active interactions

### 6. Avatar Integration

- Handle HeyGen connection separately from Agent C connection
- Synchronize avatar speech with text display
- Provide fallback UI when avatar is unavailable

## Troubleshooting

### Common Issues

1. **Connection Refused**
   
   - Verify JWT token is valid and not expired
   - Check WebSocket URL format
   - Ensure network connectivity

2. **Agent/Avatar Not Found**
   
   - Verify agent key exists in available agents list
   - Check avatar ID against available avatars list
   - Ensure proper session setup order

3. **Messages Not Streaming**
   
   - Check event handler registration
   - Verify interaction state management
   - Look for JavaScript errors in console

4. **Avatar Not Speaking**
   
   - Verify HeyGen session establishment
   - Check avatar connection event received
   - Ensure text deltas contain newlines for speech triggers

### Debug Mode

```javascript
class DebugAgentCClient extends AgentCChatClient {
    constructor(jwtToken, baseUrl) {
        super(jwtToken, baseUrl);
        this.debugMode = true;
    }

    handleMessage(event) {
        if (this.debugMode) {
            console.log('🔍 Debug - Received event:', {
                type: event.type,
                timestamp: new Date().toISOString(),
                data: event
            });
        }
        super.handleMessage(event);
    }

    sendEvent(event) {
        if (this.debugMode) {
            console.log('🔍 Debug - Sending event:', {
                type: event.type,
                timestamp: new Date().toISOString(),
                data: event
            });
        }
        super.sendEvent(event);
    }
}
```

This integration guide provides practical, working examples that developers can adapt for their specific needs. For complete event specifications, refer to the [Client Events Reference](realtime_api_client_events.md) and [Runtime Events Reference](realtime_api_runtime_events.md).