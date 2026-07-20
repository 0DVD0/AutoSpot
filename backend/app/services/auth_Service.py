from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.authDTO import LoginData, TokenResponse, RefreshTokenRequest
from app.schemas.userDTO import UserCreate
from app.repositories.user_Repository import get_user_by_email, get_user_by_username, create_user
from app.repositories.refresh_token_Repository import create_refresh_token, revoke_refresh_token, revoke_all_user_refresh_tokens, get_refresh_token_by_id
from app.core.security import split_refresh_token, verify_password, create_access_token, hash_password, get_refresh_token_expiration, verify_refresh_token_secret, build_refresh_token, hash_refresh_token_secret, generate_refresh_token_secret
from app.models.user import User

def create_token_pair(db: Session, user_id: int) -> TokenResponse:
    access_token = create_access_token(subject=str(user_id))

    refresh_secret = generate_refresh_token_secret()
    refresh_secret_hash = hash_refresh_token_secret(refresh_secret)
    refresh_expires_at = get_refresh_token_expiration()

    refresh_token_row = create_refresh_token(
        db=db,
        user_id=user_id,
        secret_hash=refresh_secret_hash,
        expires_at=refresh_expires_at,
    )

    refresh_token = build_refresh_token(
        token_id=refresh_token_row.id,
        secret=refresh_secret,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

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
    
    tokens = create_token_pair(db, user.id)
    return tokens

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


def refresh(db: Session, refresh_data: RefreshTokenRequest) -> TokenResponse:
    try:
        token_id, secret = split_refresh_token(refresh_data.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    stored_token = get_refresh_token_by_id(db, token_id)

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token was revoked",
        )

    if stored_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    if not verify_refresh_token_secret(secret, stored_token.secret_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    revoke_refresh_token(db, stored_token.id)

    return create_token_pair(db, stored_token.user_id)

def logout(db: Session, refresh_data: RefreshTokenRequest) -> bool:
    try:
        token_id, secret = split_refresh_token(refresh_data.refresh_token)
    except ValueError:
        return True

    stored_token = get_refresh_token_by_id(db, token_id)

    if stored_token is None:
        return True

    if stored_token.revoked_at is None:
        revoke_refresh_token(db, stored_token.id)

    return True