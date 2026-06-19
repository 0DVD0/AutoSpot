from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.post import Post
from app.repositories import post_Repository, user_Repository
from app.schemas.postDTO import PostCreate

def get_feed(db: Session) -> list[Post]:
    now = datetime.now(timezone.utc)

    posts = post_Repository.get_posts(db, now)
    return posts

def create_post(db: Session, post: PostCreate) -> Post:
    if(user_Repository.get_user_by_id(post.user_id) is None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no user with that id"
        )
    created_post = post_Repository.create_post(post, db)
    return created_post

def get_post(post_id: int, db: Session) -> Post | None:
    now = datetime.now(timezone.utc)
    post = post_Repository.get_post(post_id, db, now)
    return post