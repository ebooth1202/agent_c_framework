from typing import Any, Literal

from pydantic import BaseModel as BM, ConfigDict
from pydantic.main import IncEx

class BaseModel(BM):
    model_config = ConfigDict(extra="forbid")
