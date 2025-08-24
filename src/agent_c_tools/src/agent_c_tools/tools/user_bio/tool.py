from typing import Any, Union

from agent_c.toolsets import json_schema, Toolset
from .prompt import UserBioSection, UserBioSectionNoToolUse

class UserBioTools(Toolset):
    """
    Allows your agent to learn and remember personal information about you, such as your name and preferences.
    This helps your agent provide more personalized interactions and maintain relevant context about who you are
    across different conversations and sessions.
    """

    def __init__(self, **kwargs: Any):
        """Initialize MemoryTools with a MemorySection instance.

        Args:
            **kwargs (Any): Keyword arguments including those for ZepDependentToolset.
        """
        super().__init__(**kwargs, name='userbio', need_tool_user=False)

        if self.agent_can_use_tools:
            section_cls = UserBioSection
        else:
            section_cls = UserBioSectionNoToolUse

        self.section = kwargs.get('section', section_cls(session_manager=self.session_manager))

    @json_schema(
        (
            'Update the first and/or last name in the user record for the current chat user.'
        ),
        {
            'first': {
                'type': 'string',
                'description': "The user's first name",
                'required': False
            },
            'last': {
                'type': 'string',
                'description': "The user's last name.",
                'required': False
            }
        }
    )
    async def update_name(self, **kwargs: Any) -> str:
        first: Union[str, None] = kwargs.get("first", None)
        last: Union[str, None] = kwargs.get("last", None)

        if first is not None:
            self.session_manager.user.first_name = first

        if last is not None:
            self.session_manager.user.last_name = last

        if first is None and last is None:
            return "You need to supply `first` and/or `last` to update"

        return "User records updated"

# This is broken so disabling it.
# Toolset.register(UserBioTools)
