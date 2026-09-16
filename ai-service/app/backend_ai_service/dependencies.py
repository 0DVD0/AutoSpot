from fastapi import Request
from app.post_image_service import PostImageService

def get_post_image_service(request: Request) -> PostImageService:
    return request.app.state.post_image_service