# Agent Configuration API

## Overview

The Agent Configuration API allows you to manage the configuration of an AI agent within a specific session. This includes retrieving the current configuration and updating various parameters that control the agent's behavior.

Agent configuration parameters determine how the AI agent responds to user inputs, what tools it can use, and how it generates responses. Properly configuring these parameters is essential for optimizing the agent's performance for different use cases.

## Authentication

All agent configuration endpoints require authentication. Include your API key in all requests:

```
Authorization: Bearer YOUR_API_KEY
```

## Agent Configuration Lifecycle

Agent configuration follows this lifecycle:

1. **Initial Configuration**: Set during session creation with the parameters in the SessionCreate model
2. **Configuration Retrieval**: Get the current configuration using the Get Agent Configuration endpoint
3. **Configuration Updates**: Modify the configuration as needed using the Update Agent Configuration endpoint
4. **Verification**: After updates, you can retrieve the configuration again to verify changes

## Endpoints

### Get Agent Configuration

```http
GET /api/v2/sessions/{session_id}/agent
```

Retrieves the current configuration of the agent associated with the specified session.

#### Path Parameters

| Parameter   | Type   | Description              | Required |
|------------|--------|---------------------------|----------|
| session_id | UUID   | The unique session ID     | Yes      |

#### Response

```json
{
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "custom_prompt": null,
  "temperature": 0.7,
  "reasoning_effort": 5,
  "budget_tokens": null,
  "max_tokens": 2000,
  "tools": ["search", "code_analysis", "calculator"]
}
```

#### Response Fields

| Field           | Type     | Description                                          |
|-----------------|----------|------------------------------------------------------|
| model_id        | string   | ID of the LLM model being used                       |
| persona_id      | string   | ID of the persona being used                         |
| custom_prompt   | string   | Custom prompt overriding the persona (if any)        |
| temperature     | number   | Temperature parameter for the model (0.0 to 1.0)     |
| reasoning_effort| number   | Reasoning effort parameter for OpenAI (0 to 10)      |
| budget_tokens   | number   | Budget tokens parameter for Claude models            |
| max_tokens      | number   | Maximum tokens for model output                      |
| tools           | string[] | List of enabled tool IDs                             |

#### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 200         | Success                                       |
| 404         | Session not found                             |
| 500         | Server error                                  |

#### Example Request

```python
import requests
from uuid import UUID

api_key = "YOUR_API_KEY"
session_id = UUID("550e8400-e29b-41d4-a716-446655440000")

response = requests.get(
    f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}/agent",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    agent_config = response.json()
    print(f"Agent is using {agent_config['model_id']} with {agent_config['persona_id']} persona")
    print(f"Temperature: {agent_config['temperature']}")
    print(f"Tools enabled: {', '.join(agent_config['tools'])}")
```

```javascript
// Using fetch in JavaScript
const apiKey = 'YOUR_API_KEY';
const sessionId = '550e8400-e29b-41d4-a716-446655440000';

fetch(`https://your-agent-c-instance.com/api/v2/sessions/${sessionId}/agent`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(agentConfig => {
  console.log(`Agent is using ${agentConfig.model_id} with ${agentConfig.persona_id} persona`);
  console.log(`Temperature: ${agentConfig.temperature}`);
  console.log(`Tools enabled: ${agentConfig.tools.join(', ')}`);
})
.catch(error => console.error('Error fetching agent config:', error));
```

#### Error Response

```json
{
  "detail": "Session 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### Update Agent Configuration

```http
PATCH /api/v2/sessions/{session_id}/agent
```

Updates one or more configuration parameters of the agent associated with the specified session. Returns the updated configuration along with details about which changes were applied.

#### Path Parameters

| Parameter   | Type   | Description              | Required |
|------------|--------|---------------------------|----------|
| session_id | UUID   | The unique session ID     | Yes      |

#### Request Body

```json
{
  "temperature": 0.8,
  "persona_id": "researcher",
  "reasoning_effort": 7
}
```

#### Request Fields

| Field           | Type     | Description                                          | Required |
|-----------------|----------|------------------------------------------------------|----------|
| persona_id      | string   | ID of the persona to use                             | No       |
| custom_prompt   | string   | Custom prompt overriding the persona                 | No       |
| temperature     | number   | Temperature parameter (0.0 to 1.0)                   | No       |
| reasoning_effort| number   | Reasoning effort parameter (0 to 10, for OpenAI)     | No       |
| budget_tokens   | number   | Budget tokens parameter (for Claude)                 | No       |
| max_tokens      | number   | Maximum tokens for model output                      | No       |

#### Response

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
    "tools": ["search", "code_analysis", "calculator"]
  },
  "changes_applied": {
    "temperature": {
      "from": 0.7,
      "to": 0.8
    },
    "persona_id": {
      "from": "programmer",
      "to": "researcher"
    },
    "reasoning_effort": {
      "from": 5,
      "to": 7
    }
  },
  "changes_skipped": {}
}
```

#### Response Fields

| Field           | Type     | Description                                          |
|-----------------|----------|------------------------------------------------------|
| agent_config    | object   | The complete updated agent configuration             |
| changes_applied | object   | Map of parameters that were successfully updated, showing 'from' and 'to' values for each change |
| changes_skipped | object   | Map of parameters that were skipped, with reasons    |

#### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 200         | Success                                       |
| 404         | Session not found                             |
| 422         | Validation error                              |
| 500         | Server error                                  |

#### Example Request

```python
import requests
from uuid import UUID

api_key = "YOUR_API_KEY"
session_id = UUID("550e8400-e29b-41d4-a716-446655440000")

# Update the agent's persona and temperature
update_data = {
    "persona_id": "researcher",
    "temperature": 0.8,
    "reasoning_effort": 7
}

response = requests.patch(
    f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}/agent",
    json=update_data,
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    result = response.json()
    config = result["agent_config"]
    changes = result["changes_applied"]
    
    print(f"Updated to {config['persona_id']} persona")
    print("Changes applied:", changes)
```

```javascript
// Using fetch in JavaScript
const apiKey = 'YOUR_API_KEY';
const sessionId = '550e8400-e29b-41d4-a716-446655440000';

const updateData = {
  persona_id: 'researcher',
  temperature: 0.8,
  reasoning_effort: 7
};

fetch(`https://your-agent-c-instance.com/api/v2/sessions/${sessionId}/agent`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(updateData)
})
.then(response => response.json())
.then(result => {
  const config = result.agent_config;
  const changes = result.changes_applied;
  
  console.log(`Updated to ${config.persona_id} persona`);
  console.log('Changes applied:', changes);
})
.catch(error => console.error('Error updating agent config:', error));
```

#### Validation Error Response

```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

## Configuration Parameters

### Model Parameters

#### temperature

Controls randomness in the agent's responses. Lower values (e.g., 0.2) make responses more deterministic and focused, while higher values (e.g., 0.8) make them more creative and diverse.

- **Valid range**: 0.0 to 1.0
- **Default**: Model-dependent (typically 0.7)
- **Example use case**: Lower for factual tasks, higher for creative tasks

#### reasoning_effort

Applies to OpenAI models. Controls how much effort the model puts into reasoning through complex problems. Higher values result in more thorough reasoning but may increase response time and token usage.

- **Valid range**: 0 to 10
- **Default**: 5
- **Example use case**: Higher for complex problem solving tasks

#### budget_tokens

Applies to Claude models. Sets a budget for the number of tokens the model should aim to use for thinking.

- **Valid range**: >= 0
- **Default**: Model-dependent
- **Example use case**: Higher for complex tasks, lower for simple queries

#### max_tokens

Limits the maximum number of tokens in the model's response.

- **Valid range**: >= 0
- **Default**: Model-dependent (typically 2000)
- **Example use case**: Lower for concise responses, higher for detailed explanations

### Persona Control

#### persona_id

Specifies the persona the agent should adopt, which determines its tone, style, and domain expertise.

- **Valid values**: Any persona ID configured in the system
- **Default**: "default"
- **Examples**: "programmer", "researcher", "teacher"

#### custom_prompt

Provides a custom prompt that overrides the persona definition. This allows for completely custom agent behavior.

- **Valid values**: Any string
- **Default**: null (uses the persona)
- **Example use case**: When you need specialized behavior not covered by existing personas

## Best Practices

### Optimizing Agent Performance

1. **Match parameters to task complexity**
   - Use higher reasoning_effort and temperature for complex, creative tasks
   - Use lower values for factual, straightforward tasks
   
2. **Carefully select personas**
   - Choose personas that match your domain (e.g., programmer persona for code tasks)
   - Consider switching personas when changing domains
   
3. **Update incrementally**
   - Change one parameter at a time to understand its effect
   - Verify the impact after each change
   
4. **Monitor changes_skipped**
   - Review the changes_skipped field to understand why some updates weren't applied
   - Fix validation issues and retry

### Parameter Combinations

Some parameter combinations work particularly well for specific tasks:

- **Code Review**: programmer persona, temperature 0.2, reasoning_effort 8
- **Creative Writing**: writer persona, temperature 0.8, reasoning_effort 5
- **Data Analysis**: researcher persona, temperature 0.4, reasoning_effort 7
- **Factual Q&A**: teacher persona, temperature 0.3, reasoning_effort 6