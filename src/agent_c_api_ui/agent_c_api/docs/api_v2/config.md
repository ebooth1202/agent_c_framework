# Configuration Endpoints

The configuration endpoints provide read-only access to system configuration data, including available models, personas, and tools. These endpoints are designed to be used for initializing client applications and do not require authentication.

## Authentication

Configuration endpoints are the only endpoints in the API that do not require authentication. This allows client applications to retrieve configuration data before a user is logged in.

## Common Parameters

No common query parameters are used across configuration endpoints.

## Common Response Format

All configuration endpoints return data in a consistent format, typically with the resource name as the top-level key:

```json
{
  "resource_name": [
    {
      "id": "resource-id",
      "name": "Resource Name",
      // Additional resource properties...
    }
  ]
}
```

## Error Handling

Configuration endpoints may return the following error responses:

- `404 Not Found`: When a specific resource (model, persona, or tool) doesn't exist

```json
{
  "detail": {
    "error": "RESOURCE_NOT_FOUND",
    "error_code": "RESOURCE_NOT_FOUND",
    "message": "Resource {id} not found",
    "params": {"id": "resource-id"}
  }
}
```

- `500 Internal Server Error`: When an unexpected error occurs during configuration retrieval

```json
{
  "detail": {
    "error": "Failed to retrieve configuration",
    "error_code": "CONFIG_RETRIEVAL_ERROR",
    "message": "Error message details"
  }
}
```

## Models

### List Models

```http
GET /api/v2/config/models
```

Returns a list of available LLM models that can be used with Agent C.

#### Description

This endpoint provides information about all language models configured for use with Agent C. It includes details such as model capabilities, configuration parameters, and input types.

#### Parameters

None

#### Response

**Status Code:** 200 OK

**Response Body:**

```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "OpenAI's most advanced model",
      "provider": "openai",
      "capabilities": ["text", "images", "reasoning"],
      "parameters": [
        {
          "name": "temperature",
          "type": "float",
          "description": "Controls randomness in the output. Higher values produce more creative results.",
          "default": 0.7
        },
        {
          "name": "max_tokens",
          "type": "integer",
          "description": "Maximum length of generated content",
          "default": 2048
        }
      ],
      "allowed_inputs": ["text", "image"]
    },
    {
      "id": "claude-3",
      "name": "Claude 3",
      "description": "Anthropic's most capable multimodal model",
      "provider": "anthropic",
      "capabilities": ["text", "images"],
      "parameters": [
        {
          "name": "temperature",
          "type": "float",
          "description": "Controls randomness",
          "default": 0.5
        }
      ],
      "allowed_inputs": ["text", "image"]
    }
  ]
}
```

#### Example Usage

```python
import requests

# Get all available models
response = requests.get("https://your-agent-c-instance.com/api/v2/config/models")
if response.status_code == 200:
    models = response.json()["models"]
    for model in models:
        print(f"{model['name']} ({model['id']}) - Provider: {model['provider']}")
```

```javascript
// JavaScript fetch example
fetch('https://your-agent-c-instance.com/api/v2/config/models')
  .then(response => response.json())
  .then(data => {
    const models = data.models;
    models.forEach(model => {
      console.log(`${model.name} (${model.id}) - Provider: ${model.provider}`);
    });
  })
  .catch(error => console.error('Error fetching models:', error));
```

### Get Model Details

```http
GET /api/v2/config/models/{model_id}
```

Returns detailed information about a specific language model.

#### Description

This endpoint provides detailed information about a specific language model identified by its ID. It includes full details about capabilities, configuration parameters, and supported input types.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_id` | string | **Required**. The unique identifier of the model to retrieve |

#### Response

**Status Code:** 200 OK

**Response Body:**

```json
{
  "id": "gpt-4",
  "name": "GPT-4",
  "description": "OpenAI's most advanced model, with broader general knowledge and advanced reasoning capabilities.",
  "provider": "openai",
  "capabilities": ["text", "images", "reasoning"],
  "parameters": [
    {
      "name": "temperature",
      "type": "float",
      "description": "Controls randomness in the output. Higher values produce more creative results.",
      "default": 0.7
    },
    {
      "name": "max_tokens",
      "type": "integer",
      "description": "Maximum length of generated content",
      "default": 2048
    }
  ],
  "allowed_inputs": ["text", "image"]
}
```

#### Error Responses

**Status Code:** 404 Not Found

Returned when the requested model doesn't exist.

```json
{
  "detail": {
    "error": "MODEL_NOT_FOUND",
    "error_code": "MODEL_NOT_FOUND",
    "message": "Model gpt-99 not found",
    "params": {"model_id": "gpt-99"}
  }
}
```

#### Example Usage

```python
import requests

model_id = "gpt-4"
response = requests.get(f"https://your-agent-c-instance.com/api/v2/config/models/{model_id}")

if response.status_code == 200:
    model = response.json()
    print(f"Model: {model['name']} ({model['id']})
    print(f"Provider: {model['provider']}
    print(f"Description: {model['description']}
    print(f"Capabilities: {', '.join(model['capabilities'])}
    print("Parameters:")
    for param in model['parameters']:
        print(f"  - {param['name']}: {param['description']} (default: {param['default']})")
else:
    error = response.json().get("detail", {})
    print(f"Error: {error.get('message', 'Unknown error')}")
```

## Personas

### List Personas

```
GET /api/v2/config/personas
```

Returns a list of available personas.

**Response Example:**

```json
{
  "personas": [
    {
      "id": "coder",
      "name": "Coding Assistant",
      "description": "Specialized in writing and reviewing code",
      "file_path": "/path/to/coder.md",
      "content": "You are a coding assistant..."
    }
  ]
}
```

### Get Persona Details

```
GET /api/v2/config/personas/{persona_id}
```

Returns detailed information about a specific persona.

**Path Parameters:**

- `persona_id`: The ID of the persona to retrieve

**Response Example:**

```json
{
  "id": "coder",
  "name": "Coding Assistant",
  "description": "Specialized in writing and reviewing code",
  "file_path": "/path/to/coder.md",
  "content": "You are a coding assistant..."
}
```

## Tools

### List Tools

```
GET /api/v2/config/tools
```

Returns a list of available tools.

**Response Example:**

```json
{
  "tools": [
    {
      "id": "web_search",
      "name": "Web Search",
      "description": "Search the web for information",
      "category": "web",
      "parameters": [
        {
          "name": "query",
          "type": "string",
          "description": "Search query",
          "required": true
        }
      ],
      "is_essential": true
    }
  ],
  "categories": ["web", "utility"],
  "essential_tools": ["web_search"]
}
```

### Get Tool Details

```
GET /api/v2/config/tools/{tool_id}
```

Returns detailed information about a specific tool.

**Path Parameters:**

- `tool_id`: The ID of the tool to retrieve

**Response Example:**

```json
{
  "id": "web_search",
  "name": "Web Search",
  "description": "Search the web for information",
  "category": "web",
  "parameters": [
    {
      "name": "query",
      "type": "string",
      "description": "Search query",
      "required": true
    }
  ],
  "is_essential": true
}
```

### Get System Configuration

```
GET /api/v2/config/system
```

Returns a combined configuration with models, personas, and tools.

**Response Example:**

```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "openai"
    }
  ],
  "personas": [
    {
      "id": "default",
      "name": "Default Persona"
    }
  ],
  "tools": [
    {
      "id": "web_search",
      "name": "Web Search",
      "category": "web"
    }
  ],
  "tool_categories": ["web", "utility"],
  "essential_tools": ["web_search"]
}
```

## Error Responses

Configuration endpoints may return the following error responses:

- `404 Not Found`: When a requested resource (model, persona, or tool) doesn't exist
- `500 Internal Server Error`: When an unexpected error occurs