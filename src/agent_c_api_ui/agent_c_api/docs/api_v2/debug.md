# Debug API

## Overview

The Debug API provides endpoints for retrieving diagnostic information about active sessions and agents. These endpoints are designed primarily for development, troubleshooting, and administrative purposes, offering deep insights into the internal state of Agent C components.

## Authentication

All debug endpoints require authentication with admin privileges. Without proper authorization, these endpoints will return a 403 Forbidden error.

## Key Concepts

### Session Debug Information

Session debug information provides comprehensive details about a session's state, including:

- Session identifiers (both UI and internal)
- Agent configuration and model information
- Message statistics and recent message previews
- Component status information (session manager, chat session, tool chest)

### Agent Debug Information

Agent debug information exposes the configuration parameters of an active agent, including:

- Agent bridge parameters (API-facing configuration)
- Internal agent parameters (underlying implementation configuration)
- Runtime settings such as temperature, reasoning effort, and token budgets

## Endpoints

### Get Session Debug Information

```http
GET /api/v2/debug/sessions/{session_id}
```

Retrieves comprehensive debug information about a session.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| session_id | UUID | The unique identifier for the session |

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | UI session ID |
| agent_c_session_id | string | Agent C internal session ID |
| agent_name | string | Name of the agent |
| created_at | string | When the session was created |
| backend | string | LLM backend being used |
| model_name | string | Model name being used |
| session_manager | object | Debug info about the session manager |
| chat_session | object | Debug info about the chat session |
| messages | object | Debug info about messages |
| recent_messages | array | Preview of recent messages |
| current_chat_Log | object | Debug info about the current chat log |
| tool_chest | object | Debug info about the tool chest |

#### Example Response

```json
{
  "status": {
    "success": true,
    "message": "Session debug information retrieved successfully"
  },
  "data": {
    "session_id": "ui-sess-def456",
    "agent_c_session_id": "internal-sess-xyz789",
    "agent_name": "Tech Support Agent",
    "created_at": "2025-05-04T13:45:22Z",
    "backend": "openai",
    "model_name": "gpt-4",
    "session_manager": {
      "exists": true,
      "user_id": "user-12345",
      "has_chat_session": true
    },
    "chat_session": {
      "session_id": "chat-sess-abc123",
      "has_active_memory": true
    },
    "messages": {
      "count": 7,
      "user_messages": 3,
      "assistant_messages": 4,
      "latest_message": "I'll analyze that code snippet now..."
    },
    "recent_messages": [
      {
        "role": "user",
        "content_preview": "Can you help me debug my Python code...",
        "timestamp": "2025-05-04T14:22:15Z"
      },
      {
        "role": "assistant",
        "content_preview": "I'd be happy to help with your Python code...",
        "timestamp": "2025-05-04T14:22:45Z"
      }
    ],
    "current_chat_Log": {
      "exists": true,
      "count": 12
    },
    "tool_chest": {
      "exists": true,
      "active_tools": ["web_search", "code_interpreter", "file_browser"]
    }
  }
}
```

#### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Session not found |
| 500 | Internal server error |

### Get Agent Debug Information

```http
GET /api/v2/debug/agent/{session_id}
```

Retrieves detailed debug information about an agent's state and configuration.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| session_id | UUID | The unique identifier for the session containing the agent |

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| status | string | Status of the agent debug operation |
| agent_bridge_params | object | Parameters for the agent bridge |
| internal_agent_params | object | Parameters for the internal agent |

##### Agent Bridge Parameters

| Field | Type | Description |
|-------|------|-------------|
| temperature | number | Temperature for response generation (0.0-1.0) |
| reasoning_effort | string | Level of reasoning effort (minimal, moderate, thorough) |
| extended_thinking | boolean | Whether extended thinking is enabled |
| budget_tokens | integer | Token budget for the agent |
| max_tokens | integer | Maximum tokens for responses |

##### Internal Agent Parameters

| Field | Type | Description |
|-------|------|-------------|
| type | string | Type of the internal agent |
| temperature | number | Temperature for response generation (0.0-1.0) |
| reasoning_effort | string | Level of reasoning effort |
| budget_tokens | integer | Token budget for the agent |
| max_tokens | integer | Maximum tokens for responses |

#### Example Response

```json
{
  "status": {
    "success": true,
    "message": "Agent debug information retrieved successfully"
  },
  "data": {
    "status": "success",
    "agent_bridge_params": {
      "temperature": 0.7,
      "reasoning_effort": "thorough",
      "extended_thinking": true,
      "budget_tokens": 8000,
      "max_tokens": 4000
    },
    "internal_agent_params": {
      "type": "ReactJSAgent",
      "temperature": 0.5,
      "reasoning_effort": "thorough",
      "budget_tokens": 8000,
      "max_tokens": 4000
    }
  }
}
```

#### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Session or agent not found |
| 500 | Internal server error |

## Usage Examples

### Python Example: Getting Session Debug Information

```python
import requests

# Authentication
auth_response = requests.post(
    "https://your-agent-c-instance.com/api/auth/login",
    json={"username": "admin", "password": "your_admin_password"}
)

token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get session debug info
session_id = "123e4567-e89b-12d3-a456-426614174000"
response = requests.get(
    f"https://your-agent-c-instance.com/api/v2/debug/sessions/{session_id}",
    headers=headers
)

if response.status_code == 200:
    debug_info = response.json()["data"]
    print(f"Session has {debug_info['messages']['count']} messages")
    print(f"Using model: {debug_info['model_name']}")
    
    # Check if certain tools are active
    active_tools = debug_info["tool_chest"]["active_tools"]
    if "code_interpreter" in active_tools:
        print("Code interpreter is active")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript Example: Getting Agent Debug Information

```javascript
async function getAgentDebugInfo(sessionId) {
  // Authentication
  const authResponse = await fetch('https://your-agent-c-instance.com/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'your_admin_password' })
  });
  
  const authData = await authResponse.json();
  const token = authData.access_token;
  
  // Get agent debug info
  const response = await fetch(`https://your-agent-c-instance.com/api/v2/debug/agent/${sessionId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    const data = await response.json();
    console.log('Agent type:', data.data.internal_agent_params.type);
    console.log('Temperature:', data.data.agent_bridge_params.temperature);
    console.log('Reasoning effort:', data.data.agent_bridge_params.reasoning_effort);
    return data.data;
  } else {
    console.error('Error:', response.status, await response.text());
    return null;
  }
}

// Usage
getAgentDebugInfo('123e4567-e89b-12d3-a456-426614174000')
  .then(debugInfo => {
    if (debugInfo) {
      // Use debug info for troubleshooting
    }
  });
```

## Administrative Considerations

### Security

The Debug API exposes sensitive internal information about the Agent C system. Access should be strictly limited to administrators and developers. Consider implementing additional security measures such as:

- IP filtering to limit access to specific networks
- Comprehensive audit logging of all debug API access
- Time-limited access tokens for temporary debugging sessions

### Performance Impact

Debug endpoints perform comprehensive data gathering which may have a performance impact during high load scenarios. Consider the following guidelines:

- Avoid frequent polling of debug endpoints in production environments
- Implement rate limiting specific to debug endpoints
- Use debug endpoints sparingly during performance-sensitive operations

### Troubleshooting Use Cases

The debug endpoints are particularly useful for the following troubleshooting scenarios:

1. **Agent Configuration Issues**: Verifying that agent parameters are correctly set
2. **Session State Problems**: Diagnosing issues with session initialization or state management
3. **Tool Availability**: Confirming which tools are available to an agent session
4. **Message Processing**: Investigating message delivery or response generation problems
5. **Performance Analysis**: Examining configuration parameters that might affect performance