# Models API

> **Documentation generated**: May 1, 2025

Endpoints for accessing available models and their capabilities.

## List Available Models

```
GET /api/v1/models
```

Retrieves a list of all available models with their capabilities and parameters.

### Response

| Field | Type | Description |
|-------|------|-------------|
| `models` | array | List of available models |
| `models[].id` | string | Model identifier |
| `models[].label` | string | Display name for the model |
| `models[].description` | string | Description of the model |
| `models[].model_type` | string | Model type (e.g., 'chat', 'reasoning') |
| `models[].backend` | string | Backend provider (e.g., 'openai', 'claude') |
| `models[].parameters` | object | Available configuration parameters |
| `models[].parameters.{param_name}` | object | Configuration for a specific parameter |
| `models[].parameters.{param_name}.default` | any | Default value for the parameter |
| `models[].parameters.{param_name}.min` | number | Minimum value (for numeric parameters) |
| `models[].parameters.{param_name}.max` | number | Maximum value (for numeric parameters) |
| `models[].parameters.{param_name}.required` | boolean | Whether the parameter is required |
| `models[].capabilities` | object | Model capabilities |
| `models[].capabilities.supports_tools` | boolean | Whether the model supports tools |
| `models[].capabilities.multi_modal` | boolean | Whether the model supports multi-modal inputs |
| `models[].allowed_inputs` | object | Supported input types |
| `models[].allowed_inputs.image` | boolean | Whether the model accepts image inputs |
| `models[].allowed_inputs.video` | boolean | Whether the model accepts video inputs |
| `models[].allowed_inputs.audio` | boolean | Whether the model accepts audio inputs |
| `models[].allowed_inputs.file` | boolean | Whether the model accepts file inputs |

#### Response Example

```json
{
  "models": [
    {
      "id": "gpt-4o",
      "label": "GPT-4o",
      "description": "GPT-4 OpenAI model for chat interactions.",
      "model_type": "chat",
      "backend": "openai",
      "parameters": {
        "temperature": {
          "default": 0.5,
          "min": 0,
          "max": 2,
          "required": true
        },
        "max_tokens": {
          "min": 1000,
          "max": 16384,
          "default": 16384,
          "required": false
        }
      },
      "capabilities": {
        "supports_tools": true,
        "multi_modal": true
      },
      "allowed_inputs": {
        "image": true,
        "video": false,
        "audio": false,
        "file": false
      }
    },
    {
      "id": "claude-3-5-sonnet-latest",
      "label": "Claude 3.5 Sonnet",
      "description": "Anthropic's Claude 3.5 Sonnet model for advanced reasoning.",
      "model_type": "chat",
      "backend": "claude",
      "parameters": {
        "temperature": {
          "default": 0.7,
          "min": 0,
          "max": 1,
          "required": true
        },
        "max_tokens": {
          "min": 1000,
          "max": 8192,
          "default": 8192,
          "required": false
        },
        "budget_tokens": {
          "min": 0,
          "max": 100000,
          "default": 0,
          "required": false
        }
      },
      "capabilities": {
        "supports_tools": true,
        "multi_modal": true
      },
      "allowed_inputs": {
        "image": true,
        "video": false,
        "audio": false,
        "file": false
      }
    }
  ]
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 500 | Internal Server Error - Error reading model configuration |