from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.post import Post
from app.schemas.postDTO import  PostRead, PostCreate

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.get("", response_model=list[PostRead])
def get_posts(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    statements = (
        select(Post).where(Post.is_active == True).where(Post.expires_at > now).order_by(Post.created_at.desc())
    )

    posts = db.scalars(statements).all()
    return posts

@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    post = Post(**post_data.model_dump())

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    statement = (
        select(Post).where(Post.id == post_id).where(Post.is_active == True).where(Post.expires_at > now)
    )

    post = db.scalars(statement).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found!"
        )
    return post
