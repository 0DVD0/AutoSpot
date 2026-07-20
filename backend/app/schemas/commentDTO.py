from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class CommentCreate(BaseModel):
    content: str = Field(min_lenght=1, max_length=500)

class CommentAuthor(BaseModel):
    id: int
    username: str
    avatar_url: HttpUrl | None = None

    model_config = {
        "from_attributes":True
    }

class CommentRead(BaseModel):
    id: int
    post_id:int
    user_id: int
    content: str
    created_at: datetime
    user: CommentAuthor 

    model_config = {
        "from_attributes": True
    }