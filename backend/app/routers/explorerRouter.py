from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.postDTO import  PostRead, PostCreate
from app.schemas.commentDTO import CommentRead, CommentCreate
from app.schemas.likeDTO import LikeStatus, LikeRead
from app.services import post_Service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/explore",
    tags=["explore"]
)

@router.get("/posts", response_model=list[PostRead])
def get_explore_posts(min_lat: Annotated[float, Query(ge=-90, le=90)], max_lat: Annotated[float, Query(ge=-90, le=90)], min_lng: Annotated[float, Query(ge=-180,le=180)], max_lng: Annotated[float, Query(ge=-180, le=180)], limit: Annotated[int, Query(ge=1, le=200)] = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post_Service.get_explore_feed(db, current_user, min_lat, max_lat, min_lng, max_lng, limit)


@router.get("/recent", response_model=list[PostRead])
def get_recent_posts(limit: Annotated[int, Query(ge=1, le=200)], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post_Service.get_recent_posts(db, current_user, limit)