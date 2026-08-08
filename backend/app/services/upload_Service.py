from uuid import uuid4
from fastapi import HTTPException, UploadFile, status
from supabase import Client, create_client
from app.core.config import settings
from app.models.post import Post
from app.schemas.uploadDTO import UploadRead

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp"
}

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

def upload_post_image(file: UploadFile, user_id: int) -> UploadRead:
    content_type = file.content_type

    if content_type not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This format is not supported"
        )
    
    file_content = file.file.read(MAX_IMAGE_SIZE + 1)

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request"
        )
    
    if len(file_content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image too large"
        )
    
    extention = ALLOWED_IMAGE_FORMATS[content_type]
    file_name = f"{uuid4()}{extention}"
    storage_path = f"users/{user_id}/{file_name}"

    try:
        bucket = supabase.storage.from_(
            settings.supabase_post_images_bucket
        )
        bucket.upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": content_type,
                "cache-control": "3600",
                "upsert": "false"
            }
        )

        image_url = bucket.get_public_url(storage_path)

    except Exception as error:
        print(
            "Supabase upload error:",
            type(error).__name__,
            str(error),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not upload image"
        ) from error
    return UploadRead(image_url=image_url, storage_path=storage_path)

def delete_post_image(storage_path: str) -> None:
    try:
        supabase.storage.from_(
            settings.supabase_post_images_bucket
        ).remove([storage_path])
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not remove image"
        ) from error
    
def remove_expired_posts_images(posts: list[Post]):
    posts_paths = []
    for post in posts:
        posts_paths.append(post.image_storage_path)
    if not posts_paths:
        return
    try:
        supabase.storage.from_(
            settings.supabase_post_images_bucket
        ).remove(posts_paths)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not remove images"
        ) from error

def delete_avatar_image(storage_path: str) -> None:
    try:
        supabase.storage.from_(
            settings.supabase_avatar_image_bucket
        ).remove([storage_path])
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not remove image"
        ) from error

def upload_avatar_image(file: UploadFile, user_id: int):
    content_type = file.content_type
    
    if content_type not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This format is not supported"
        )
    
    file_content = file.file.read(MAX_IMAGE_SIZE + 1)

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request"
        )
    
    if len(file_content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image too large"
        )
    
    extention = ALLOWED_IMAGE_FORMATS[content_type]
    file_name = f"{uuid4()}{extention}"
    storage_path = f"users/{user_id}/{file_name}"

    try:

        bucket = supabase.storage.from_(
            settings.supabase_avatar_image_bucket
        )
        bucket.upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": content_type,
                "cache-control": "3600",
                "upsert": "false"
            }
        )

        image_url = bucket.get_public_url(storage_path)

    except Exception as error:
        print(
            "Supabase upload error:",
            type(error).__name__,
            str(error),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not upload image"
        ) from error
    return UploadRead(image_url=image_url, storage_path=storage_path)

