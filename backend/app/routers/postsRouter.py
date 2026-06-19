from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.postDTO import  PostRead, PostCreate
from app.services import post_Service

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.get("", response_model=list[PostRead])
def get_posts(db: Session = Depends(get_db)):
    return post_Service.get_feed(db)

@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    return post_Service.create_post(db, post_data)

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_Service.get_post(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found!"
        )
    return post
