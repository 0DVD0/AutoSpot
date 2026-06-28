from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_Repository, follow_Repository
from app.schemas.userDTO import UserCreate
from app.schemas.followDTO import FollowStatus

def build_follow_status(db: Session, target_user_id: int, current_user_id: int) -> FollowStatus:
    return FollowStatus(
        user_id=target_user_id,
        followers_count=follow_Repository.count_followers(db, target_user_id),
        following_count=follow_Repository.count_following(db, target_user_id),
        is_followed_by_me=follow_Repository.is_followed_by_user(
            db,
            target_user_id=target_user_id,
            current_user_id=current_user_id,
        ),
    )

def get_users(db: Session) -> list[User]:
  
    users = user_Repository.get_users(db)
    return users

def get_user(user_id: int, db: Session) -> User | None:
    user = user_Repository.get_user_by_id(db, user_id)
    return user

def follow_user(db: Session, to_follow_id: int, curent_user: User) ->FollowStatus:
    user = get_user(to_follow_id, db)

    if (user is None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if (user.id == curent_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't follow yourself" 
        )
    
    existing_follow = follow_Repository.get_follow(
        db,
        follower_id=curent_user.id,
        following_id=user.id,
    )

    if existing_follow is None:
        follow_Repository.create_follow(db, curent_user.id, user.id)

    return build_follow_status(db, user.id, curent_user.id)

def unfollow_user(db: Session, to_unfollow_id: int, curent_user: User) -> FollowStatus:
    user = get_user(to_unfollow_id, db)

    if (user is None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if (user.id == curent_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't unfollow yourself" 
        )
    
    follow_Repository.remove_follow(db, curent_user.id, user.id)
    
    return build_follow_status(db, user.id, curent_user.id)