from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.user import User
from app.models.interactions.like import Like
from app.repositories import post_Repository, user_Repository, like_Repository, comment_Repository
from app.schemas.postDTO import PostCreate
from app.schemas.likeDTO import LikeStatus
from app.models.interactions.comment import Comment
from app.schemas.commentDTO import CommentCreate

def add_post_social_status(db: Session, post: Post, current_user: User) -> Post:
    post.likes_count = like_Repository.count_likes(db, post.id)
    post.comments_count = comment_Repository.count_comments(db, post.id)
    post.is_liked_by_me = like_Repository.is_liked_by_user(db, post.id, current_user.id)
    return post

def add_posts_social_status(db: Session, posts: list[Post], current_user: User) -> list[Post]:
    for post in posts:
        add_post_social_status(db, post, current_user)

    return posts

def get_feed(db: Session, current_user: User) -> list[Post]:
    now = datetime.now(timezone.utc)

    post_Repository.deactivate_expired_posts(db, now)
    posts = post_Repository.get_posts(db, now)
    return add_posts_social_status(db, posts, current_user)

def remove_user_post(db: Session, post_id: int, current_user: User) -> bool:
    deleted_count = post_Repository.remove_user_post_by_id(db, post_id, current_user.id)

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you do not have permission to delete it"
        )

    return True

def create_post(db: Session, post: PostCreate, current_user: User ) -> Post:
    
    created_post = post_Repository.create_post(post, db, current_user.id)
    now = datetime.now(timezone.utc)
    post_with_user = post_Repository.get_post(created_post.id, db, now)

    if post_with_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found after creation",
        )

    return add_post_social_status(db, post_with_user, current_user)

def get_post(post_id: int, db: Session, current_user: User) -> Post | None:
    now = datetime.now(timezone.utc)
    post = post_Repository.get_post(post_id, db, now)
    if post is None:
        return None

    add_post_social_status(db, post, current_user)
    return post

def toggle_like_post(db: Session, post_id: int, current_user: User) -> LikeStatus:
    now = datetime.now(timezone.utc)

    post = post_Repository.get_post(post_id, db, now)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    existing_like = like_Repository.get_like(db, post_id, current_user.id)

    if existing_like is not None:
        like_Repository.remove_like(db, post_id, current_user.id)

        return LikeStatus(
            post_id=post_id,
            likes_count=like_Repository.count_likes(db, post_id),
            is_liked_by_me=False,
        )

    like_Repository.create_like(db, post_id, current_user.id)

    return LikeStatus(
        post_id=post_id,
        likes_count=like_Repository.count_likes(db, post_id),
        is_liked_by_me=True,
    )
    
def get_post_likes(db: Session, post_id: int) -> list[Like]:
    now = datetime.now(timezone.utc)
    post = post_Repository.get_post(post_id, db, now)
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
            )
        
    likes = like_Repository.get_likes(db, post.id)
    return likes

def get_post_comments(db: Session, post_id: int) -> list[Comment]:
    now = datetime.now(timezone.utc)

    post = post_Repository.get_post(post_id, db, now)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return comment_Repository.get_comments_by_post(db, post_id)


def create_comment(
    db: Session,
    post_id: int,
    comment_data: CommentCreate,
    current_user: User,
) -> Comment:
    now = datetime.now(timezone.utc)

    post = post_Repository.get_post(post_id, db, now)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    comment = comment_Repository.create_comment(
        db=db,
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    return comment


def delete_comment(db: Session, post_id: int, comment_id: int, current_user: User) -> bool:
    now = datetime.now(timezone.utc)

    post = post_Repository.get_post(post_id, db, now)
    comment = comment_Repository.get_comment_by_id(db, comment_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.post_id != post.id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )
    
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    deleted_count = comment_Repository.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
    )

    return deleted_count > 0
