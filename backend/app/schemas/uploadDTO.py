from pydantic import BaseModel, HttpUrl

class UploadRead(BaseModel):
    image_url: HttpUrl
    storage_path: str
