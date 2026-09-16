from base64 import b64encode
from io import BytesIO
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from PIL import Image, UnidentifiedImageError

from app.backend_ai_service.dependencies import get_post_image_service
from app.identification_service import (NoVehicleDetectedError)
from app.post_image_service import PostImageService
from app.backend_ai_service.schemas.image_processing import ProcessImageRead


MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/process", response_model=ProcessImageRead)
def process_image(file: Annotated[UploadFile, File()], service: PostImageService = Depends(get_post_image_service)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image type unsopported"
        )

    image_content = file.file.read(MAX_IMAGE_SIZE + 1)

    if not image_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image"
        )

    if len(image_content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size is too large"
        )

    try:
        with Image.open(BytesIO(image_content)) as source_image:
            source_image.load()
            image = source_image.copy()
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Invalid image"
        ) from error
    try:
        result = service.process(image)
    except NoVehicleDetectedError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error)
        ) from error

    encoded_image = b64encode(result.processed_image).decode("ascii")

    return ProcessImageRead(identification=result.identification, processed_image_base64=encoded_image, content_type="image/jpeg", plates_detected=len(result.plate_detections))