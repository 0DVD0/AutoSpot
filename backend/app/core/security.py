from datetime import datetime, timedelta, timezone
import secrets
from app.core.config import settings
from passlib.context import CryptContext
from jose import jwt
from uuid import UUID

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

def generate_refresh_token_secret() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token_secret(secret: str) -> str:
    return password_context.hash(secret)


def verify_refresh_token_secret(plain_secret: str, hashed_secret: str) -> bool:
    return password_context.verify(plain_secret, hashed_secret)


def build_refresh_token(token_id: str, secret: str) -> str:
    return f"{token_id}.{secret}"


def split_refresh_token(refresh_token: str) -> tuple[str, str]:
    parts = refresh_token.split(".", 1)

    if len(parts) != 2:
        raise ValueError("Invalid refresh token format")

    token_id, secret = parts

    if not token_id or not secret:
        raise ValueError("Invalid refresh token format")

    try:
        UUID(token_id)
    except ValueError:
        raise ValueError("Invalid refresh token id")

    return token_id, secret


def get_refresh_token_expiration() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )