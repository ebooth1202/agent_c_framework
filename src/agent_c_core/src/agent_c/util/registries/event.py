from typing import Dict, Type, Optional

from agent_c.util import to_snake_case


class EventRegistry:
    _registry: Dict[str, Type['BaseEvent']] = {}

    @classmethod
    def register(cls, event_class: Type['BaseEvent']):
        event_type = to_snake_case(event_class.__name__.removesuffix('Event'))
        cls._registry[event_type] = event_class

    @classmethod
    def get_class(cls, event_type: str) -> Optional[Type['BaseEvent']]:
        return cls._registry.get(event_type)

    @classmethod
    def list_types(cls) -> list:
        return list(cls._registry.keys())
