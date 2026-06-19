from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None


class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = {
        'from_attributes':True
    }