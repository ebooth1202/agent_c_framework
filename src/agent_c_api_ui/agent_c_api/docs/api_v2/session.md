# Session Management API

## Overview

The Session Management API allows you to create, retrieve, update, and delete AI agent sessions. Sessions are the core concept in the Agent C platform, representing an ongoing conversation with an AI agent configured with specific parameters.

Each session has:
- A unique identifier (UUID)
- An associated AI model and persona
- Configuration parameters that determine the agent's behavior
- A lifecycle from creation to deletion

## Authentication

All session management endpoints require authentication. Include your API key in all requests:

```
Authorization: Bearer YOUR_API_KEY
```

## Session Lifecycle

Sessions follow this lifecycle:

1. **Creation**: A new session is created with specific parameters
2. **Initialization**: The agent is initialized with the specified configuration
3. **Active Use**: The session is used for interactions (via the Chat API)
4. **Updates**: The session's configuration may be updated during its lifetime
5. **Deletion**: The session is terminated and its resources are released

Sessions remain active until explicitly deleted or until they expire (based on system settings).

## Endpoints

### Create Session

```http
POST /api/v2/sessions
```

Creates a new AI agent session with the specified configuration parameters.

#### Request Body

```json
{
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "name": "Code Review Session",
  "temperature": 0.7,
  "reasoning_effort": 5,
  "max_tokens": 2000,
  "tools": ["search", "code_analysis", "calculator"],
  "metadata": {
    "project": "API Redesign",
    "priority": "high"
  }
}
```

#### Request Fields

| Field           | Type     | Description                                          | Required |
|-----------------|----------|------------------------------------------------------|----------|
| model_id        | string   | ID of the LLM model to use                           | Yes      |
| persona_id      | string   | ID of the persona to use                             | No       |
| name            | string   | User-friendly session name                           | No       |
| custom_prompt   | string   | Custom prompt overriding the persona                 | No       |
| temperature     | number   | Temperature parameter (0.0 to 1.0)                   | No       |
| reasoning_effort| number   | Reasoning effort parameter (0 to 10, for OpenAI)     | No       |
| budget_tokens   | number   | Budget tokens parameter (for Claude)                 | No       |
| max_tokens      | number   | Maximum tokens for model output                      | No       |
| tools           | string[] | List of tool IDs to enable                           | No       |
| metadata        | object   | Additional metadata for the session                  | No       |

#### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "name": "Code Review Session",
  "created_at": "2025-04-01T14:30:00Z",
  "updated_at": "2025-04-01T14:30:00Z",
  "last_activity": "2025-04-01T14:30:00Z",
  "is_active": true,
  "agent_internal_id": "agent-internal-54321",
  "tools": ["search", "code_analysis", "calculator"],
  "tool_ids": ["search", "code_analysis", "calculator"],
  "temperature": 0.7,
  "reasoning_effort": 5,
  "max_tokens": 2000,
  "custom_prompt": null,
  "metadata": {
    "project": "API Redesign",
    "priority": "high"
  },
  "message_count": 0
}
```

#### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 201         | Session created successfully                  |
| 400         | Invalid request parameters                    |
| 500         | Server error                                  |

#### Example Request

```python
import requests

api_key = "YOUR_API_KEY"

session_data = {
    "model_id": "gpt-4",
    "persona_id": "programmer",
    "name": "Code Review Session",
    "temperature": 0.7,
    "tools": ["search", "code_analysis"]
}

response = requests.post(
    "https://your-agent-c-instance.com/api/v2/sessions",
    json=session_data,
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 201:
    session = response.json()
    print(f"Created session {session['id']} named {session['name']}")
```

```javascript
// Using fetch in JavaScript
const apiKey = 'YOUR_API_KEY';

const sessionData = {
  model_id: 'gpt-4',
  persona_id: 'programmer',
  name: 'Code Review Session',
  temperature: 0.7,
  tools: ['search', 'code_analysis']
};

fetch('https://your-agent-c-instance.com/api/v2/sessions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(sessionData)
})
.then(response => response.json())
.then(session => {
  console.log(`Created session ${session.id} named ${session.name}`);
})
.catch(error => console.error('Error creating session:', error));
```

### List Sessions

```http
GET /api/v2/sessions
```

Retrieves a paginated list of all active sessions.

#### Query Parameters

| Parameter | Type    | Description                               | Required | Default |
|-----------|---------|-------------------------------------------|----------|--------|
| limit     | integer | Maximum number of sessions to return      | No       | 10     |
| offset    | integer | Number of sessions to skip for pagination | No       | 0      |

#### Response

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "model_id": "gpt-4",
      "persona_id": "programmer",
      "name": "Code Review Session",
      "created_at": "2025-04-01T14:30:00Z",
      "updated_at": "2025-04-01T16:45:00Z",
      "last_activity": "2025-04-01T16:45:00Z",
      "is_active": true
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "model_id": "claude-3-opus",
      "persona_id": "researcher",
      "name": "Data Analysis",
      "created_at": "2025-04-02T09:15:00Z",
      "updated_at": "2025-04-02T11:20:00Z",
      "last_activity": "2025-04-02T11:20:00Z",
      "is_active": true
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

#### Response Fields

| Field      | Type      | Description                                 |
|------------|-----------|---------------------------------------------|
| items      | array     | List of session summaries                    |
| total      | integer   | Total number of sessions across all pages    |
| limit      | integer   | Maximum number of sessions per page          |
| offset     | integer   | Current offset in the full result set        |

#### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 200         | Success                                       |
| 500         | Server error                                  |

#### Example Request

```python
import requests

api_key = "YOUR_API_KEY"

# Get first page of sessions (10 per page)
response = requests.get(
    "https://your-agent-c-instance.com/api/v2/sessions",
    params={"limit": 10, "offset": 0},
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    result = response.json()
    sessions = result["items"]
    total = result["total"]
    
    print(f"Showing {len(sessions)} of {total} total sessions")
    
    # Get next page if there are more sessions
    if total > 10:
        next_page = requests.get(
            "https://your-agent-c-instance.com/api/v2/sessions",
            params={"limit": 10, "offset": 10},
            headers={"Authorization": f"Bearer {api_key}"}
        )
```

### Get Session

```http
GET /api/v2/sessions/{session_id}
```

Retrieves detailed information about a specific session.

#### Path Parameters

| Parameter   | Type   | Description              | Required |
|------------|--------|---------------------------|----------|
| session_id | UUID   | The unique session ID     | Yes      |

#### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "model_id": "gpt-4",
  "persona_id": "programmer",
  "name": "Code Review Session",
  "created_at": "2025-04-01T14:30:00Z",
  "updated_at": "2025-04-01T16:45:00Z",
  "last_activity": "2025-04-01T16:45:00Z",
  "is_active": true,
  "agent_internal_id": "agent-internal-54321",
  "tools": ["search", "code_analysis", "calculator"],
  "tool_ids": ["search", "code_analysis", "calculator"],
  "temperature": 0.7,
  "reasoning_effort": 5,
  "max_tokens": 2000,
  "custom_prompt": null,
  "metadata": {
    "project": "API Redesign",
    "priority": "high"
  },
  "message_count": 12
}
```

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
    f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    session = response.json()
    print(f"Session {session['name']} is using model {session['model_id']}")
    print(f"Last activity: {session['last_activity']}")
```

### Update Session

```http
PATCH /api/v2/sessions/{session_id}
```

Updates one or more properties of a specific session.

#### Path Parameters

| Parameter   | Type   | Description              | Required |
|------------|--------|---------------------------|----------|
| session_id | UUID   | The unique session ID     | Yes      |

#### Request Body

```json
{
  "name": "Refactoring Session",
  "persona_id": "architect",
  "temperature": 0.8,
  "metadata": {
    "project": "API Redesign",
    "phase": "implementation"
  }
}
```

#### Request Fields

| Field           | Type     | Description                                          | Required |
|-----------------|----------|------------------------------------------------------|----------|
| name            | string   | New session name                                     | No       |
| persona_id      | string   | ID of the persona to switch to                       | No       |
| custom_prompt   | string   | Custom prompt overriding the persona                 | No       |
| temperature     | number   | Temperature parameter (0.0 to 1.0)                   | No       |
| reasoning_effort| number   | Reasoning effort parameter (0 to 10, for OpenAI)     | No       |
| budget_tokens   | number   | Budget tokens parameter (for Claude)                 | No       |
| max_tokens      | number   | Maximum tokens for model output                      | No       |
| metadata        | object   | Metadata to update or add                            | No       |

#### Response

The response is the complete updated session details, in the same format as the GET session response.

#### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 200         | Success                                       |
| 404         | Session not found                             |
| 400         | Invalid request parameters                    |
| 500         | Server error                                  |

#### Example Request

```python
import requests
from uuid import UUID

api_key = "YOUR_API_KEY"
session_id = UUID("550e8400-e29b-41d4-a716-446655440000")

# Update the session name and temperature
update_data = {
    "name": "Refactoring Session",
    "temperature": 0.8
}

response = requests.patch(
    f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}",
    json=update_data,
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    updated_session = response.json()
    print(f"Session renamed to {updated_session['name']}")
    print(f"Temperature updated to {updated_session['temperature']}")
```

### Delete Session

```http
DELETE /api/v2/sessions/{session_id}
```

Permanently removes a session and releases its resources.

#### Path Parameters

| Parameter   | Type   | Description              | Required |
|------------|--------|---------------------------|----------|
| session_id | UUID   | The unique session ID     | Yes      |

#### Response

No content is returned for successful deletion (204 status code).

#### Status Codes

| Status Code | Description                                   |
|-------------|-----------------------------------------------|
| 204         | Session successfully deleted                  |
| 404         | Session not found                             |
| 500         | Server error                                  |

#### Example Request

```python
import requests
from uuid import UUID

api_key = "YOUR_API_KEY"
session_id = UUID("550e8400-e29b-41d4-a716-446655440000")

response = requests.delete(
    f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 204:
    print("Session successfully deleted")
elif response.status_code == 404:
    print("Session not found")
else:
    print(f"Error: {response.text}")
```

## Session Parameters

### Name and Identification

#### session_id

The unique identifier for the session. This is automatically generated when a session is created.

- **Format**: UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
- **Usage**: Use this ID in all API calls that target a specific session

#### name

A user-friendly name for the session. If not provided at creation, a default name is generated.

- **Default**: Generated based on timestamp and model
- **Example**: "Code Review Session"

### Agent Configuration

#### model_id

Specifies which large language model to use for the session.

- **Required**: Yes (at creation)
- **Common values**: "gpt-4", "claude-3-opus", "gemini-1.0-pro"

#### persona_id

Specifies the persona the agent should adopt, affecting its tone, style, and domain expertise.

- **Default**: "default"
- **Common values**: "programmer", "researcher", "teacher"

#### custom_prompt

Allows you to override the persona with a completely custom prompt.

- **Default**: null (uses the persona)
- **Example**: "You are an expert in Python performance optimization..."

### Model Parameters

#### temperature

Controls randomness in the agent's responses.

- **Range**: 0.0 to 1.0
- **Default**: Model-dependent (typically 0.7)

#### reasoning_effort

Applies to OpenAI models. Controls reasoning thoroughness.

- **Range**: 0 to 10
- **Default**: 5

#### budget_tokens

Applies to Claude models. Sets token budget for thinking.

- **Range**: >= 0
- **Default**: Model-dependent

#### max_tokens

Limits the maximum tokens in responses.

- **Range**: >= 0
- **Default**: Model-dependent (typically 2000)

### Tools and Extensions

#### tools

List of tool IDs that the agent can use during the session.

- **Format**: Array of strings
- **Common tools**: "search", "code_analysis", "calculator"

### Metadata

#### metadata

Custom metadata associated with the session. This can be any JSON object and is useful for client-side organization and filtering.

- **Format**: JSON object
- **Example**: `{"project": "API Redesign", "priority": "high"}`

## Best Practices

### Session Management

1. **Use meaningful session names**
   - Choose descriptive names that indicate the purpose of the session
   - Consider including project names or task types in the name
   
2. **Clean up unused sessions**
   - Delete sessions that are no longer needed to free up resources
   - Consider implementing a session archiving strategy for important conversations
   
3. **Use metadata for organization**
   - Add metadata to help categorize and filter sessions
   - Include project identifiers, user information, or priority levels

### Configuration Optimization

1. **Match model to task complexity**
   - Use more advanced models (e.g., GPT-4) for complex tasks
   - Use simpler models for straightforward tasks to reduce latency
   
2. **Start with default parameters**
   - Begin with default values for temperature and reasoning parameters
   - Adjust incrementally based on the quality of responses
   
3. **Choose appropriate personas**
   - Select personas that match your domain
   - Use custom prompts only when existing personas don't fit your needs

### Session Lifecycle Management

1. **Create sessions with a clear purpose**
   - Each session should focus on a specific task or topic
   - Avoid using one session for multiple unrelated tasks
   
2. **Update sessions as context changes**
   - Adjust parameters if the conversation shifts to a new domain
   - Consider creating a new session if the topic changes significantly
   
3. **Monitor session activity**
   - Check last_activity timestamps to identify stale sessions
   - Archive or delete sessions that haven't been used for an extended period