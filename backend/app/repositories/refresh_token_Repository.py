from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.security.refresh_token import RefreshToken


def create_refresh_token(db: Session, user_id: int, secret_hash: str, expires_at: datetime ):
    token = RefreshToken(
        user_id = user_id,
        secret_hash = secret_hash,
        expires_at = expires_at
    )

    db.add(token)
    db.commit()
    db.refresh(token)

    return token

def get_refresh_token_by_id(
    db: Session,
    refresh_token_id: str,
) -> RefreshToken | None:
    statement = (
        select(RefreshToken)
        .where(RefreshToken.id == refresh_token_id)
    )

    return db.scalars(statement).first()


def revoke_refresh_token(
    db: Session,
    refresh_token_id: str,
) -> int:
    statement = (
        update(RefreshToken)
        .where(RefreshToken.id == refresh_token_id)
        .where(RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc))
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount


def revoke_all_user_refresh_tokens(
    db: Session,
    user_id: int,
) -> int:
    statement = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .where(RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc))
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount