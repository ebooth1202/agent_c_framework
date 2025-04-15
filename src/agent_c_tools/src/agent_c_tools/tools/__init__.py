# Register all tools for the agent

from . import workspace
from . import web
from . import web_search
from . import memory
from . import think
from . import mermaid_chart
from . import user_bio
from . import weather
from . import random_number
from . import xml_explorer  # New XML Explorer toolset

__all__ = [
    'workspace',
    'web', 
    'web_search', 
    'memory',
    'think',
    'mermaid_chart',
    'user_bio',
    'weather',
    'random_number',
    'xml_explorer',  # Add to __all__ list
]