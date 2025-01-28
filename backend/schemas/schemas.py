from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import asyncio

class InputData(BaseModel):
    prune_measure: int 
    prune_quantiles: int
    h3_zoom: int = 10
    sliders: list[int]
    buffer_walk_distance: int


class ModelTask(BaseModel):
    task : Optional[asyncio.Task] = Field(default=None, exclude=True)
    user: str
    start_time: str

    model_config = ConfigDict(arbitrary_types_allowed=True)