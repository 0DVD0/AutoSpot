from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class LikeStatus(BaseModel):
    post_id: int
    likes_count: int
    is_liked_by_me: bool

class LikeUser(BaseModel):
    id: int
    username: str
    avatar_url: HttpUrl | None = None

    model_config = {
        "from_attributes": True
    }

class LikeRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    user: LikeUser

    model_config = {
        "from_attributes": True
    }
