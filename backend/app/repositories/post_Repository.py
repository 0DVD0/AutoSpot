from datetime import datetime, timezone
from sqlalchemy import func, select, delete, update
from sqlalchemy.orm import Session, selectinload
from app.models.post import Post
from app.schemas.postDTO import PostCreate
def remove_expired_posts(db: Session, now: datetime) -> int:
    statement = (
        delete(Post).where(Post.expires_at <= now)
    )

    result = db.execute(statement)
    db.commit()
    return result.rowcount

def deactivate_expired_posts(db: Session, now: datetime) -> int:
    statement = (
        update(Post).where(Post.is_active.is_(True)).where(Post.expires_at <= now).values(is_active=False)
    )
    result = db.execute(statement)
    db.commit()
    return result.rowcount

def remove_user_post_by_id(db: Session, post_id: int, user_id: int) -> int:
    statement = (
        delete(Post).where(Post.id == post_id).where(Post.user_id == user_id)
    )
    result = db.execute(statement)
    db.commit()
    return result.rowcount
def get_posts(db: Session, now: datetime) -> list[Post]:

    statements = (
        select(Post).options(selectinload(Post.user)).where(Post.is_active.is_(True)).where(Post.expires_at > now).order_by(Post.created_at.desc())
    )

    posts = list(db.scalars(statements).all())
    return posts

def create_post(post_data: PostCreate, db: Session, user_id: int) -> Post:
    post = Post(**post_data.model_dump(mode="json"), user_id = user_id)

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

def get_post(post_id: int, db: Session, now: datetime) -> Post | None:
    statement = (
        select(Post)
        .options(selectinload(Post.user))
        .where(Post.id == post_id)
        .where(Post.is_active.is_(True))
        .where(Post.expires_at > now)
    )

    post = db.scalars(statement).first()

    return post

def get_posts_by_user_id(db: Session, user_id: int, now: datetime) -> list[Post]:
    statement = (
        select(Post).options(selectinload(Post.user)).where(Post.user_id == user_id).where(Post.expires_at >  now).where(Post.is_active.is_(True)).order_by(Post.created_at.desc())
    )

    posts = list(db.scalars(statement).all())
    return posts

def count_user_posts(db: Session, user_id: int, now: datetime) -> int:
    statement = (
        select(func.count())
        .select_from(Post)
        .where(Post.user_id == user_id)
        .where(Post.is_active.is_(True))
        .where(Post.expires_at > now)
    )

    return db.scalar(statement) or 0