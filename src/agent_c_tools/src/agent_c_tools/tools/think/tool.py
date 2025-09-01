from agent_c.toolsets import Toolset, json_schema

class ThinkTools(Toolset):
    """
    Provides your agent with a dedicated space for reflection and complex reasoning. The agent can use this
    to work through difficult problems step-by-step, organize its thoughts, and maintain context for
    multi-step tasks without cluttering the main conversation.
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
