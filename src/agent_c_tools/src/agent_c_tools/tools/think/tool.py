from agent_c.toolsets import Toolset, json_schema

class ThinkTools(Toolset):
    """
    A simple toolset that allows Claude to think about something.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='think', use_prefix=False)


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
        return ''


Toolset.register(ThinkTools)
