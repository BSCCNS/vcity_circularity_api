from pydantic import BaseModel


class InputData(BaseModel):
    prune_measure: int 
    prune_quantiles: int
    h3_zoom: int = 10
    sliders: list[int]
    buffer_walk_distance: int


class ModelTask(BaseModel):
    task: object
    user: str
    start_time: str