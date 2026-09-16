from typing import Literal
from pydantic import BaseModel, Field
from app.identification_schema import IdentificationResult

class ProcessImageRead(BaseModel):
    identification: IdentificationResult
    processed_image_base64: str
    content_type: Literal["image/jpeg"]
    plates_detected: int = Field(ge=0)