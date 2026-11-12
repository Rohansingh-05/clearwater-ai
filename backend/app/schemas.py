from pydantic import BaseModel, Field
from typing import Literal

class WaterSample(BaseModel):
    sample_name: str = Field(default="Untitled sample", max_length=100)
    ph: float = Field(ge=0, le=14)
    dissolved_oxygen: float = Field(ge=0, le=30)
    turbidity: float = Field(ge=0, le=5000)
    tds: float = Field(ge=0, le=100000)
    contamination: Literal[0, 1, 2] = Field(description="0=none reported, 1=suspected, 2=detected")
