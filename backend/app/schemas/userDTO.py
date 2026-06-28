from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    avatar_url: HttpUrl | None = None
    bio: str | None = Field(min_length=None, max_length= 100)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=20)

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = {
        'from_attributes':True
    }