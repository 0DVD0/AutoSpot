from pydantic import BaseModel, HttpUrl
from typing import Literal

class UploadRead(BaseModel):
    image_url: HttpUrl
    storage_path: str
    ai_status: Literal["suggested", "brand_only", "not_identified", "unavailable"]
    brand: str | None
    model: str | None
    plates_blurred: int
