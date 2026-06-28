from app.models.interactions.follow import Follow
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session, selectinload

def get_follow(db: Session, follower_id: int, following_id: int) -> Follow | None:
    statement = (
        select(Follow)
        .where(Follow.follower_id == follower_id)
        .where(Follow.following_id == following_id)
    )

    return db.scalars(statement).first()

def create_follow(db: Session, follower_id: int, following_id: int) -> Follow:
    follow = Follow(follower_id = follower_id, following_id = following_id)

    db.add(follow)
    db.commit()
    db.refresh(follow)

    return follow

def remove_follow(db: Session, user_id: int, following_id: int) -> int:
    statement = (
        delete(Follow).where(Follow.follower_id == user_id).where(Follow.following_id == following_id)
    )
    result = db.execute(statement)
    db.commit()
    return result.rowcount

def get_followers(db: Session, user_id: int) -> list[Follow]:

    statements = (
        select(Follow).options(selectinload(Follow.follower)).where(Follow.following_id == user_id).order_by(Follow.created_at.desc())
    )

    followers = list(db.scalars(statements).all())
    return followers

def count_followers(db: Session, user_id: int) -> int:
    statement = (
        select(func.count())
        .select_from(Follow)
        .where(Follow.following_id == user_id)
    )

    return db.scalar(statement) or 0

def count_following(db: Session, user_id: int) -> int:
    statement = (
        select(func.count())
        .select_from(Follow)
        .where(Follow.follower_id == user_id)
    )

    return db.scalar(statement) or 0

def is_followed_by_user(db: Session, target_user_id: int, current_user_id: int) -> bool:
    return get_follow(
        db,
        follower_id=current_user_id,
        following_id=target_user_id,
    ) is not None


def get_following(db: Session, user_id: int) -> list[Follow]:
    statement = (
        select(Follow)
        .options(selectinload(Follow.following))
        .where(Follow.follower_id == user_id)
        .order_by(Follow.created_at.desc())
    )

    return list(db.scalars(statement).all())