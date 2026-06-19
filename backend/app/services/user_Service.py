from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_Repository
from app.schemas.userDTO import UserCreate

def get_users(db: Session) -> list[User]:
  
    users = user_Repository.get_users(db)
    return users

def create_user(db: Session, user_data: UserCreate) -> User:
    if(user_Repository.get_user_by_email(db, user_data.email) is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already is used"
        )

    if(user_Repository.get_user_by_username(db, user_data.username) is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already is used"
        )
    hashed_password = hash_password(user_data.password)
    user = user_Repository.create_user(db, user_data, hashed_password)
    return user

def get_user(user_id: int, db: Session) -> User | None:
    user = user_Repository.get_user_by_id(user_id, db)
    return user