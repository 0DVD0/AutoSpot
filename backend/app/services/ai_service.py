from base64 import b64decode
from binascii import Error as Base64Error
from dataclasses import dataclass
import httpx

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings


from app.schemas.aiDTO import AIIdentificationRead, AIProcessImageRead

@dataclass(frozen=True)
class ProcessedPostImage:
    image_bytes: bytes
    content_type: str
    identification: AIIdentificationRead
    plates_detected: int

def process_post_image(image_content: bytes, file_name: str, content_type: str):
    try: 
        response = httpx.post(
            (f"{settings.ai_service_url}/images/process"),
            files= {"file": (file_name, image_content, content_type)},
            timeout=settings.ai_service_timeout
        )   
        response.raise_for_status()
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Ai processing timed out"
        ) from error

    except httpx.HTTPStatusError as error:
        if error.response.status_code == 422:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No vehicle could be found"
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service returned an error"
        ) from error

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not connect to AI service"
        )

    try:
        response_data = (AIProcessImageRead.model_validate(response.json()))

        processed_bytes = b64decode(response_data.processed_image_base64, validate=True)

    except (ValidationError, ValueError, Base64Error) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from AI service"
        ) from error

    if not processed_bytes:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service returned an empty image"
        )

    return ProcessedPostImage(
        image_bytes=processed_bytes,
        content_type=response_data.content_type,
        identification=response_data.identification,
        plates_detected=response_data.plates_detected
    )