# Personas API

> **Documentation generated**: May 1, 2025

Endpoints for accessing and managing agent personas.

## List Personas

```
GET /api/v1/personas
```

Retrieves a list of all available personas.

### Response

| Field | Type | Description |
|-------|------|-------------|
| (array) | array | List of persona objects |
| [].name | string | Persona name (derived from filename or subdirectory path) |
| [].content | string | Full content of the persona markdown file |
| [].file | string | Filename of the persona file |

#### Response Example

```json
[
  {
    "name": "default",
    "content": "# Default Persona\n\nYou are a helpful AI assistant...",
    "file": "default.md"
  },
  {
    "name": "helpful - assistant",
    "content": "# Helpful Assistant\n\nYou are an exceptionally helpful and friendly AI assistant...",
    "file": "assistant.md"
  },
  {
    "name": "coding - python",
    "content": "# Python Coding Assistant\n\nYou are an expert Python developer...",
    "file": "python.md"
  }
]
```

### Notes

- Personas in subdirectories will have their path converted to a name with separators
- For example, a file at `personas/coding/python.md` would have name `coding - python`

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 500 | Internal Server Error - Error reading personas directory |