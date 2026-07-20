from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.userDTO import  UserRead, UserCreate
from app.schemas.authDTO import TokenResponse, LoginData, RefreshTokenRequest
from app.services import auth_Service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return auth_Service.register(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginData, db: Session = Depends(get_db)):
    token = auth_Service.login(db, login_data)
    return token

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest, db:Session = Depends(get_db)):
    return auth_Service.refresh(db, refresh_data)

@router.post("/logout", response_model=bool)
def logout(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return auth_Service.logout(db, refresh_data)