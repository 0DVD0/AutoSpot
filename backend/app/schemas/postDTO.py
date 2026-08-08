from pydantic import BaseModel, HttpUrl, Field, model_validator
from datetime import datetime
from typing import Literal, Self

LocationVisibility = Literal[
    "public",
    "approximate",
    "private"
]

class PostBase(BaseModel):
    image_url: HttpUrl
    brand: str | None = Field(min_length=None, max_length=10)
    model: str | None = Field(min_length=None, max_length=70)
    ai_confidence: float | None = None
    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )
    longitude: float | None = Field(
        default= None,
        ge=-180,
        le=180
    )
    location_visibility: LocationVisibility = "approximate"

class PostCreate(PostBase):
    image_storage_path: str

    @model_validator(mode="after")
    def validate_location(self) -> Self:
        one_coordinate_exists = (
            (self.latitude is None)
            !=
            (self.longitude is None)
        )

        if one_coordinate_exists:
            raise ValueError(
                "Latitude and longitude must be provided"
            )
        if (self.location_visibility != "private") and (self.latitude is None or self.longitude is None):
            raise ValueError(
                "Location is required for a visible post"
            )
        return self
    
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

