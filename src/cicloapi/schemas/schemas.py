#schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import asyncio

class InputData(BaseModel):
    city: list[str] = ["viladecans","Viladecans, Barcelona, Spain;esp","viladecans"]
    prune_measure: str = "betweeness"
    prune_quantiles: int = 40
    h3_zoom: int = 10
    sliders: list[int] = [1,2,2,3,4,5]
    buffer_walk_distance: int = 500


class ModelTask(BaseModel):
    task : Optional[asyncio.Task] = Field(default=None, exclude=True)
    user: str
    start_time: str

    model_config = ConfigDict(arbitrary_types_allowed=True)