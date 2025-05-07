# src/agent_c_api/api/v2/models/__init__.py
"""
API v2 models package.

This package contains all the Pydantic models used in the v2 API.
Model organization:
- session_models.py: Contains core session and agent configuration models
- agent_models.py: Contains models specific to agent capabilities and info
- chat_models.py: Contains message and chat-related models
- tool_models.py: Contains tool-related models
- file_models.py: Contains file and document-related models
- history_models.py: Contains models for interaction history
- response_models.py: Contains common response structure models
- debug_models.py: Contains debug and diagnostic models

IMPORTANT: When using agent configuration models (AgentConfig, AgentUpdate):
  - Always import from session_models.py, not agent_models.py
  - agent_models.py re-exports these from session_models.py to maintain compatibility
"""

# Core models
from .response_models import *
from .session_models import *
from .agent_models import *
from .tool_models import *
from .chat_models import *
from .file_models import *
from .history_models import *
from .debug_models import *