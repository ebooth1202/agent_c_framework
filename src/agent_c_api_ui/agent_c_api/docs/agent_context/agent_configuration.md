# Agent Configuration API

> **Documentation generated**: May 1, 2025

Endpoints for configuring and managing agent settings and tools.

## Update Agent Settings

```
POST /api/v1/update_settings
```

Updates settings for an existing agent session.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID to update |
| `persona_name` | string | No | Name of the persona to use |
| `custom_prompt` | string | No | Custom prompt for persona |
| `temperature` | number | No | Temperature for chat models |
| `reasoning_effort` | string | No | Reasoning effort for OpenAI models; must be 'low', 'medium', or 'high' |
| `budget_tokens` | number | No | Budget tokens (for Claude models) |

#### Request Example

```json
{
  "ui_session_id": "ses_1234567890abcdef",
  "temperature": 0.7,
  "reasoning_effort": "high"
}
```

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation, "success" if successful |
| `message` | string | Description of the result |
| `changes_made` | object | Map of changes made with from/to values |
| `skipped_null_values` | array | Parameters that were not updated (null in request) |
| `failed_updates` | array | Parameters that failed to update |

#### Response Example

```json
{
  "status": "success",
  "message": "Settings updated successfully for Agent ses_1234567890abcdef",
  "changes_made": {
    "temperature": {
      "from": "0.5",
      "to": "0.7"
    },
    "reasoning_effort": {
      "from": "medium",
      "to": "high"
    }
  },
  "skipped_null_values": [
    "custom_prompt"
  ],
  "failed_updates": []
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Invalid session ID |
| 500 | Internal Server Error - Error updating settings |

## Get Agent Configuration

```
GET /api/v1/get_agent_config/{ui_session_id}
```

Retrieves the current configuration of an agent.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `config` | object | Complete agent configuration |
| `config.user_id` | string | User ID associated with the agent |
| `config.custom_prompt` | string | Custom prompt for the agent |
| `config.ui_session_id` | string | UI session ID |
| `config.agent_c_session_id` | string | Internal Agent C session ID |
| `config.backend` | string | Backend provider (e.g., 'openai', 'claude') |
| `config.model_info` | object | Model configuration details |
| `config.model_info.name` | string | Model name |
| `config.model_info.temperature` | number | Temperature setting |
| `config.model_info.reasoning_effort` | string | Reasoning effort setting |
| `config.model_info.extended_thinking` | boolean | Whether extended thinking is enabled |
| `config.model_info.budget_tokens` | number | Budget tokens (for Claude models) |
| `config.model_info.max_tokens` | number | Maximum tokens for the model output |
| `config.initialized_tools` | array | List of tool classes initialized for the agent |
| `status` | string | Status of the operation |

#### Response Example

```json
{
  "config": {
    "user_id": "user_12345",
    "custom_prompt": "You are a helpful assistant...",
    "ui_session_id": "ses_1234567890abcdef",
    "agent_c_session_id": "agt_9876543210fedcba",
    "backend": "openai",
    "model_info": {
      "name": "gpt-4o",
      "temperature": 0.7,
      "reasoning_effort": "medium",
      "extended_thinking": false,
      "budget_tokens": 0,
      "max_tokens": 16384
    },
    "initialized_tools": [
      "WorkspaceTools",
      "ThinkTools"
    ]
  },
  "status": "success"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Error retrieving agent configuration |

## Update Agent Tools

```
POST /api/v1/update_tools
```

Updates the tools available to an agent.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |
| `tools` | array | Yes | List of tool class names to enable |

#### Request Example

```json
{
  "ui_session_id": "ses_1234567890abcdef",
  "tools": [
    "WorkspaceTools",
    "ThinkTools",
    "FileTools"
  ]
}
```

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation, "success" if successful |
| `message` | string | Description of the result |
| `active_tools` | array | List of active tools after update |
| `ui_session_id` | string | UI session ID |
| `agent_c_session_id` | string | Internal Agent C session ID |

#### Response Example

```json
{
  "status": "success",
  "message": "Tools updated successfully",
  "active_tools": [
    "WorkspaceTools",
    "ThinkTools",
    "FileTools"
  ],
  "ui_session_id": "ses_1234567890abcdef",
  "agent_c_session_id": "agt_9876543210fedcba"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid tools format |
| 404 | Not Found - Invalid session ID |
| 500 | Internal Server Error - Error updating tools |

## Get Agent Tools

```
GET /api/v1/get_agent_tools/{ui_session_id}
```

Retrieves the currently active tools for an agent.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `initialized_tools` | array | List of tool class names that are initialized for the agent |
| `status` | string | Status of the operation |

#### Response Example

```json
{
  "initialized_tools": [
    "WorkspaceTools",
    "ThinkTools",
    "FileTools"
  ],
  "status": "success"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Error retrieving tools |

## Debug Agent State

```
GET /api/v1/debug_agent_state/{ui_session_id}
```

Debug endpoint to check the state of an agent and its internal components.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation |
| `agent_bridge_params` | object | Parameters from the agent bridge |
| `agent_bridge_params.temperature` | number | Temperature setting |
| `agent_bridge_params.reasoning_effort` | string | Reasoning effort setting |
| `agent_bridge_params.extended_thinking` | boolean | Whether extended thinking is enabled |
| `agent_bridge_params.budget_tokens` | number | Budget tokens |
| `agent_bridge_params.max_tokens` | number | Maximum tokens |
| `internal_agent_params` | object | Internal agent parameters |
| `internal_agent_params.type` | string | Agent type |
| `internal_agent_params.temperature` | number | Temperature setting |
| `internal_agent_params.reasoning_effort` | string | Reasoning effort setting |
| `internal_agent_params.budget_tokens` | number | Budget tokens |
| `internal_agent_params.max_tokens` | number | Maximum tokens |

#### Response Example

```json
{
  "status": "success",
  "agent_bridge_params": {
    "temperature": 0.7,
    "reasoning_effort": "medium",
    "extended_thinking": false,
    "budget_tokens": 0,
    "max_tokens": 16384
  },
  "internal_agent_params": {
    "type": "ReactJSAgent",
    "temperature": 0.7,
    "reasoning_effort": "medium",
    "budget_tokens": 0,
    "max_tokens": 16384
  }
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Error debugging agent state |

## Debug Chat Session

```
GET /api/v1/chat_session_debug/{ui_session_id}
```

Provides debugging information for a chat session.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |

### Response

A comprehensive diagnostic information object about the chat session, including details about the agent, session manager, and message history.

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Invalid session ID |
| 500 | Internal Server Error - Error debugging session |