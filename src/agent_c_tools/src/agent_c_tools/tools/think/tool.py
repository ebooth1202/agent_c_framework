import copy
import inspect
import logging
import markdown
from typing import List, Dict, Any

from agent_c.toolsets import Toolset, json_schema


class ThinkTools(Toolset):
    """
    A simple toolset that allows reasoning models (claude) to think about something.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='think', required_tools=['workspace'], use_prefix=False)
        self.logger = logging.getLogger(__name__)

        # TODO: Remove this when the new tools go in.
        self.openai_schemas: List[Dict[str, Any]] = self.__openai_schemas()

    @json_schema(
        description='Use the tool to think about something. It will not obtain new '
                    'information or change the database, but just append the thought to the log. '
                    'Use it when complex reasoning or some cache memory is needed.',
        params={
            'thought': {
                'type': 'string',
                'description': 'A thought to think about.',
                'required': True
            }
        }
    )
    async def think(self, **kwargs) -> str:
        thought = markdown.markdown(kwargs.get('thought'))
        # await self._raise_render_media(
        #     sent_by_class=self.__class__.__name__,
        #     sent_by_function='think',
        #     content_type="text/html",
        #     content=f"<div>{thought}</div>"
        # )
        return ''

    # TODO: remove this when the new tolls go in.
    def __openai_schemas(self) -> List[Dict[str, Any]]:
        """
        Generate OpenAI-compatible schemas based on method metadata.

        Returns:
            List[Dict[str, Any]]: A list of OpenAI schemas for the registered methods in the Toolset.
        """
        openai_schemas = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, 'schema'):
                schema = copy.deepcopy(method.schema)
                openai_schemas.append(schema)

        return openai_schemas

# Register the tool
Toolset.register(ThinkTools)
