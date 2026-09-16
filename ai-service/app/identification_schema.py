from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class DetectionBox(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left: int
    top: int
    right: int
    bottom: int

class IdentificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["suggested", "brand_only", "not_identified", "unavailable"]
    brand: str | None
    model: str | None
    detection_score: float = Field(ge=0, le=1)
    detection_box: DetectionBox
    vlm_available: bool
    predictor_model: str
    detector_duration_ms: float = Field(ge=0)
    vlm_duration_ms: float = Field(ge=0)