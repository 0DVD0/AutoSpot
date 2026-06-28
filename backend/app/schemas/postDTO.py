from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class PostBase(BaseModel):
    image_url: HttpUrl
    brand: str | None = Field(min_length=None, max_length=10)
    model: str | None = Field(min_length=None, max_length=70)
    ai_confidence: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_visibility: str = "public"

class PostCreate(PostBase):
    pass
class PostAuthor(BaseModel):
    id: int
    username: str
    avatar_url: HttpUrl | None = None

    model_config = {
        "from_attributes": True
    }
class PostRead(PostBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    expires_at: datetime
    user: PostAuthor
    likes_count: int
    comments_count: int
    is_liked_by_me: bool

    model_config = {
        "from_attributes":True
    }

