from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.postDTO import PostCreate


def get_posts(db: Session, now: datetime) -> list[Post]:

    statements = (
        select(Post).where(Post.is_active.is_(True)).where(Post.expires_at > now).order_by(Post.created_at.desc())
    )

    posts = list(db.scalars(statements).all())
    return posts

def create_post(post_data: PostCreate, db: Session) -> Post:
    post = Post(**post_data.model_dump())

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

def get_post(post_id: int, db: Session, now: datetime) -> Post | None:
    statement = (
        select(Post).where(Post.id == post_id).where(Post.is_active.is_(True)).where(Post.expires_at > now)
    )

    post = db.scalars(statement).first()

    return post