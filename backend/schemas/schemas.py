from pydantic import BaseModel


class Input_Data(BaseModel):
    prune_measure: int 
    prune_quantiles: int
    h3_zoom: int = 10
    sliders: list[int]
    buffer_walk_distance: int
