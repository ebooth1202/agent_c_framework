from typing import List
from abc import ABC, abstractmethod

from .parsers import CommandParser, NoArgsParser


class Command(ABC):
    def __init__(self, parser: CommandParser = None):
        self.parser = parser or NoArgsParser()

    @property
    @abstractmethod
    def command_strings(self) -> List[str]:
        """List of command triggers, e.g., ['!exit', '!!!']"""
        pass

    @property
    @abstractmethod
    def help_text(self) -> str:
        """Description of what this command does and how to use it"""
        pass

    @abstractmethod
    async def execute(self, context, **kwargs):
        pass