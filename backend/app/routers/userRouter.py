from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.userDTO import  UserRead, UserCreate
from app.services import user_Service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    return user_Service.get_users(db)

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return user_Service.create_user(db, user_data)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_Service.get_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    return user
