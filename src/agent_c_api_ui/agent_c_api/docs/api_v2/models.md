# API v2 Models Documentation

This page provides an overview of the model organization in the Agent C API v2 and links to detailed documentation.

## Overview

The API v2 uses Pydantic models extensively for request validation, response serialization, and data transfer. Models are organized by domain and purpose, with a consistent structure and naming convention.

## Key Documentation

- [Model Organization Guide](model_organization_guide.md) - Comprehensive guide to model categories, relationships, and best practices
- [Model Usage Patterns](model_usage_patterns.md) - Examples of common usage patterns for working with models

## Model Registry

All v2 API models are registered in the `registry.py` module, which serves as a single source of truth for all models. This registry enables:

- Validation to prevent model duplication
- Documentation generation
- Dynamic model access by name or domain
- Comprehensive testing

## Model Categories

Models are organized into the following categories:

1. **Response Models** - Common response structures
2. **Session Models** - Session management and agent configuration
3. **Agent Models** - Agent capabilities and LLM models
4. **Chat Models** - Chat interactions and messages
5. **File Models** - File handling and uploads
6. **History Models** - Interaction history and session replay
7. **Tool Models** - Tool definitions and interactions
8. **Debug Models** - Debugging and diagnostics

## Key Model Relationships

![Model Relationships Diagram](./model_relationships.png)

*Note: Generate this diagram using `python tools/generate_model_graph.py`*

## Best Practices Summary

1. **Import from Source Modules** - Import models directly from their source modules whenever possible
2. **Use Registry for Discovery** - Use the registry to explore available models
3. **Proper Documentation** - Include comprehensive docstrings with relationship information
4. **Clear Naming** - Follow the established naming patterns for new models
5. **Avoid Duplication** - Use re-export pattern if a model needs to be available in multiple contexts

## Common Import Patterns

```python
# Direct import from source module (preferred)
from agent_c_api.api.v2.models.session_models import SessionDetail, AgentConfig

# Package-level import (for convenience)
from agent_c_api.api.v2.models import SessionDetail, AgentConfig

# Registry access (for dynamic model access)
from agent_c_api.api.v2.models import get_model_by_name
model_class = get_model_by_name("SessionDetail")
```

## Special Cases

**AgentConfig and AgentUpdate** - These models are defined in `session_models.py` but re-exported in `agent_models.py` for backward compatibility. Always import from `session_models.py` directly.

## Tools and Utilities

- **Model Registry**: `agent_c_api.api.v2.models.registry`
- **Diagram Generator**: `tools/generate_model_graph.py`
- **Duplication Checker**: `tools/hooks/check_model_duplication.py`

## Adding New Models

When adding new models:

1. Place in the appropriate file based on domain
2. Add to the registry by updating imports in `registry.py`
3. Document relationships with other models
4. Run the duplication checker to ensure no conflicts

See the [Model Organization Guide](model_organization_guide.md) for detailed guidance.