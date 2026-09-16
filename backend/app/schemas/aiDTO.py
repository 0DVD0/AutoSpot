from typing import Literal
from pydantic import BaseModel, Field

class AIIdentificationRead(BaseModel):
    status: Literal["suggested", "brand_only", "not_identified", "unavailable"]
    brand: str | None
    model: str | None

class AIProcessImageRead(BaseModel):
    identification: AIIdentificationRead
    processed_image_base64: str
    content_type: str
    plates_detected: int = Field(ge=0)
