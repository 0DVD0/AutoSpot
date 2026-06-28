from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class FollowUser(BaseModel):
    id: int
    username: str
    avatar_url: HttpUrl | None = None
    bio: str | None = None

    model_config = {
        "from_attributes": True
    }

class FollowStatus(BaseModel):
    user_id: int
    followers_count: int
    following_count: int
    is_followed_by_me: bool