from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import asyncio


class ModelTask(BaseModel):
    task: Optional[asyncio.Task] = Field(default=None, exclude=True)
    start_time: str
    type: str
    status: str = "Running"

    model_config = ConfigDict(arbitrary_types_allowed=True)
