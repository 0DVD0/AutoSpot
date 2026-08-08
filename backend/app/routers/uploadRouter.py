from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.uploadDTO import UploadRead
from app.services import upload_Service

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
) 

@router.post("/upload-image", response_model=UploadRead, status_code=status.HTTP_201_CREATED)
def upload_image(file: Annotated[UploadFile, File()], current_user:User = Depends(get_current_user)):
    return upload_Service.upload_post_image(file, current_user.id)