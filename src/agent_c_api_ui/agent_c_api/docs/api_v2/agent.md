# Agent Configuration API

The Agent Configuration API allows you to manage the configuration of an AI agent within a specific session. This includes retrieving the current configuration and updating various parameters that control the agent's behavior.

## Get Agent Configuration

```http
GET /api/v2/sessions/{session_id}/agent
```

Retrieves the current configuration of the agent associated with the specified session.

### Path Parameters

| Parameter   | Type   | Description              |
|------------|--------|---------------------------|
| session_id | string | The unique session ID     |

### Response

```json
{
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "custom_prompt": null,
  "temperature": 0.7,
  "reasoning_effort": 5,
  "budget_tokens": null,
  "max_tokens": 2000,
  "tools": ["search", "calculator"]
}
```

### Response Fields

| Field           | Type     | Description                                          |
|-----------------|----------|------------------------------------------------------|
| model_id        | string   | ID of the LLM model being used                       |
| persona_id      | string   | ID of the persona being used                         |
| custom_prompt   | string   | Custom prompt overriding the persona (if any)        |
| temperature     | number   | Temperature parameter for the model                  |
| reasoning_effort| number   | Reasoning effort parameter (for OpenAI)              |
| budget_tokens   | number   | Budget tokens parameter (for Claude)                 |
| max_tokens      | number   | Maximum tokens for model output                      |
| tools           | string[] | List of enabled tool IDs                             |

### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 200         | Success                                       |
| 404         | Session not found                             |
| 500         | Server error                                  |

## Update Agent Configuration

```http
PATCH /api/v2/sessions/{session_id}/agent
```

Updates one or more configuration parameters of the agent associated with the specified session. Returns the updated configuration along with details about which changes were applied.

### Path Parameters

| Parameter   | Type   | Description              |
|------------|--------|---------------------------|
| session_id | string | The unique session ID     |

### Request Body

```json
{
  "temperature": 0.8,
  "persona_id": "researcher",
  "reasoning_effort": 7
}
```

### Request Fields

| Field           | Type     | Description                                          |
|-----------------|----------|------------------------------------------------------|
| persona_id      | string   | ID of the persona to use                             |
| custom_prompt   | string   | Custom prompt overriding the persona                 |
| temperature     | number   | Temperature parameter (0.0 to 1.0)                   |
| reasoning_effort| number   | Reasoning effort parameter (0 to 10, for OpenAI)     |
| budget_tokens   | number   | Budget tokens parameter (for Claude)                 |
| max_tokens      | number   | Maximum tokens for model output                      |

### Response

```json
{
  "agent_config": {
    "model_id": "gpt-4",
    "persona_id": "researcher",
    "custom_prompt": null,
    "temperature": 0.8,
    "reasoning_effort": 7,
    "budget_tokens": null,
    "max_tokens": 2000,
    "tools": ["search", "calculator"]
  },
  "changes_applied": {
    "temperature": 0.8,
    "persona_id": "researcher",
    "reasoning_effort": 7
  },
  "changes_skipped": {}
}
```

### Response Fields

| Field           | Type     | Description                                          |
|-----------------|----------|------------------------------------------------------|
| agent_config    | object   | The complete updated agent configuration             |
| changes_applied | object   | Map of parameters that were successfully updated      |
| changes_skipped | object   | Map of parameters that were skipped                   |

### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 200         | Success                                       |
| 404         | Session not found                             |
| 422         | Validation error                              |
| 500         | Server error                                  |