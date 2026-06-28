from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.userDTO import  UserRead, UserCreate
from app.schemas.followDTO import FollowStatus
from app.models.user import User
from app.services import user_Service
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    return user_Service.get_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_Service.get_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    return user

@router.post("/{user_id}/follow", response_model=FollowStatus)
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    follow = user_Service.follow_user(db, user_id, current_user)
    return follow

@router.delete("/{user_id}/follow", response_model=FollowStatus)
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    unfollow = user_Service.unfollow_user(db, user_id, current_user )
    return unfollow
