# Agent API

> **Documentation generated**: May 1, 2025

Endpoints for initializing and managing agents.

## Initialize Agent

```
POST /api/v1/initialize
```

Creates a new agent  with the provided parameters.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_name` | string | Yes | The model name to use |
| `backend` | string | No | Backend provider (e.g., 'openai', 'claude'). Defaults based on model. |
| `persona_name` | string | No | Name of the persona to use. Default: "default" |
| `custom_prompt` | string | No | Custom prompt for persona |
| `temperature` | number | No | Temperature for chat models. Default varies by model. |
| `reasoning_effort` | string | No | Reasoning effort for OpenAI models; must be 'low', 'medium', or 'high'. Default: "medium" |
| `budget_tokens` | number | No | Budget tokens (used by some Claude models). Default: 0 |
| `max_tokens` | number | No | Maximum tokens for the model output. Default varies by model. |
| `ui_session_id` | string | No | Existing UI session ID for transferring chat history |

#### Request Example

```json
{
  "model_name": "gpt-4o",
  "backend": "openai",
  "persona_name": "default",
  "temperature": 0.7,
  "max_tokens": 8192
}
```

### Response

| Field | Type | Description |
|-------|------|-------------|
| `ui_session_id` | string | UI session ID to use for future requests |
| `agent_c_session_id` | string | Internal Agent C session ID |

#### Response Example

```json
{
  "ui_session_id": "ses_1234567890abcdef",
  "agent_c_session_id": "agt_9876543210fedcba"
}
```

### Model Validations

- For OpenAI models `o1`, `o1-mini`, `o3-mini`:
  - If `reasoning_effort` is not provided or not one of ['low', 'medium', 'high'], it defaults to 'medium'
- For Claude model `claude-3-7-sonnet-latest`:
  - If `budget_tokens` is provided, `max_tokens` will default to 64000 if not specified
  - If `budget_tokens` is not provided, it will default to 0 and `max_tokens` will default to 8192
- For chat models like 'gpt-4o', 'gpt-4o-audio-preview', 'claude-3-5-sonnet-latest':
  - For 'claude-3-5-sonnet-latest', `max_tokens` defaults to 8192 if not specified

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 500 | Internal Server Error - Error during session initialization |

## Verify Session

```
GET /api/v1/verify_session/{ui_session_id}
```

Verifies if a session exists and is valid.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID to verify |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `valid` | boolean | Whether the session is valid |

#### Response Example

```json
{
  "valid": true
}
```

## Delete All Sessions

```
DELETE /api/v1/sessions
```

Deletes all active sessions and cleans up their resources.

### Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Status of the operation, "success" if successful |
| `message` | string | Description of the result |
| `deleted_count` | number | Number of sessions deleted |

#### Response Example

```json
{
  "status": "success",
  "message": "Successfully deleted 5 sessions",
  "deleted_count": 5
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 500 | Internal Server Error - Failed to delete sessions |