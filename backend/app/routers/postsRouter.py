from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.postDTO import  PostRead, PostCreate
from app.schemas.commentDTO import CommentRead, CommentCreate
from app.schemas.likeDTO import LikeStatus, LikeRead
from app.services import post_Service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.get("", response_model=list[PostRead])
def get_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post_Service.get_feed(db, current_user)

@router.delete("/{post_id}", response_model=bool)
def remove_post(post_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    return post_Service.remove_user_post(db, post_id, current_user)

@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post_Service.create_post(db, post_data, current_user)

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = post_Service.get_post(post_id, db, current_user)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found!"
        )
    return post

@router.post("/{post_id}/like", response_model=LikeStatus)
def like_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = post_Service.toggle_like_post(db, post_id, current_user)
    return like

@router.get("/{post_id}/likes", response_model=list[LikeRead])
def get_likes(post_id: int, db: Session = Depends(get_db)):
    likes = post_Service.get_post_likes(db, post_id)
    return likes

@router.post("/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def comment_on_post(post_id: int, content: CommentCreate , db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = post_Service.create_comment(db, post_id, content, current_user)
    return comment

@router.get("/{post_id}/comments", response_model= list[CommentRead])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = post_Service.get_post_comments(db, post_id)
    return comments

@router.delete("/{post_id}/comments/{comment_id}", response_model=bool)
def remove_comment(post_id: int, comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response = post_Service.delete_comment(db, post_id, comment_id, current_user)
    return response
