from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    user_id: int
    image_url: str
    brand: str | None = None
    model: str | None = None
    ai_confidence: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_visibility: str = "public"

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    is_active: bool
    created_at: datetime
    expires_at: datetime

    model_config = {
        "from_attributes":True
    }