# Configuration Endpoints

The configuration endpoints provide read-only access to system configuration data, including available models, personas, and tools. These endpoints are designed to be used for initializing client applications and do not require authentication.

## Models

### List Models

```
GET /api/v2/config/models
```

Returns a list of available LLM models.

**Response Example:**

```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "OpenAI's most advanced model",
      "provider": "openai",
      "capabilities": ["text", "images"],
      "parameters": [
        {
          "name": "temperature",
          "type": "float",
          "description": "Controls randomness",
          "default": 0.7
        }
      ],
      "allowed_inputs": ["text"]
    }
  ]
}
```

### Get Model Details

```
GET /api/v2/config/models/{model_id}
```

Returns detailed information about a specific model.

**Path Parameters:**

- `model_id`: The ID of the model to retrieve

**Response Example:**

```json
{
  "id": "gpt-4",
  "name": "GPT-4",
  "description": "OpenAI's most advanced model",
  "provider": "openai",
  "capabilities": ["text", "images"],
  "parameters": [
    {
      "name": "temperature",
      "type": "float",
      "description": "Controls randomness",
      "default": 0.7
    }
  ],
  "allowed_inputs": ["text"]
}
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