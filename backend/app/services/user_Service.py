from datetime import datetime, timezone
from app.models.post import Post
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.repositories import post_Repository
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_Repository, follow_Repository
from app.schemas.userDTO import UserCreate, UserProfileRead, UserProfileUpdate
from app.schemas.followDTO import FollowStatus
from app.services import post_Service, upload_Service

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

def get_user_posts(db: Session, user_id: int, current_user: User) -> list[Post]:
    now = datetime.now(timezone.utc)
    user = get_user(user_id, db)
    if (user is None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    post_Repository.deactivate_expired_posts(db, now)
    posts = post_Repository.get_posts_by_user_id(db, user_id, now)
    return post_Service.add_posts_social_status(db, posts, current_user)

def build_user_profile(db: Session, user_id: int, current_user: User):
    now = datetime.now(timezone.utc)
    user = user_Repository.get_user_by_id(db, user_id)
    if (user is None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_profile = UserProfileRead(
        username = user.username, 
        email = user.email,
        avatar_url =  user.avatar_url,  
        bio = user.bio, 
        id = user.id,
        created_at = user.created_at , 
        followers_count = follow_Repository.count_followers(db, user_id) ,
        following_count = follow_Repository.count_following(db, user_id), 
        groups_count = 0,
        active_posts_count = post_Repository.count_user_posts(db, user_id, now), 
        is_followed_by_me = follow_Repository.is_followed_by_user(db, user_id, current_user.id ) ,
    )
    return user_profile

def update_user(db: Session, current_user: User, new_profile_data: UserProfileUpdate):
    if new_profile_data.username is not None:
        existing_user = user_Repository.get_user_by_username(
            db,
            new_profile_data.username,
        )

        if existing_user is not None and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username taken",
            )

    updated_user = user_Repository.patch_user(db, current_user, new_profile_data)
    return updated_user

def update_user_avatar(db: Session, current_user: User, file: UploadFile) -> User:
    old_storage_path = current_user.avatar_storage_path

    uploaded_avatar = upload_Service.upload_avatar_image(file, current_user.id)
    try:
        updated_user = user_Repository.update_user_avatar(db, current_user, str(uploaded_avatar.image_url), uploaded_avatar.storage_path)
    except Exception:
        try:
            upload_Service.delete_avatar_image(
                uploaded_avatar.storage_path
            )
        except HTTPException:
            pass

        raise
    if old_storage_path is not None:
        try: 
            upload_Service.delete_avatar_image(old_storage_path)

        except HTTPException:
            pass

    return updated_user

def remove_user_avatar(db: Session, current_user: User) -> User:
    old_storage_path = current_user.avatar_storage_path

    updated_user = user_Repository.clear_user_avatar(db, current_user)

    if old_storage_path is not None:
        try:
            upload_Service.delete_avatar_image( old_storage_path)
        except HTTPException:
            pass
    return updated_user