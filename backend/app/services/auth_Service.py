from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.authDTO import LoginData, TokenResponse
from app.schemas.userDTO import UserCreate
from app.repositories.user_Repository import get_user_by_email, get_user_by_username, create_user
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User

def login(db: Session, login_data: LoginData) -> TokenResponse:
    user = get_user_by_email(db, login_data.email)
    if(user is None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password"
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Wrong email or password"
        )
    
    access = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access)

def register(db: Session, user_data: UserCreate) -> User:
    if(get_user_by_email(db, user_data.email) is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already is used"
        )

    if(get_user_by_username(db, user_data.username) is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already is used"
        )
    hashed_password = hash_password(user_data.password)
    user = create_user(db, user_data, hashed_password)
    return user