from app.models.interactions.like import Like
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session, selectinload

def create_like(db: Session, post_id: int, user_id: int) -> Like:
    like = Like(post_id=post_id, user_id=user_id)

    db.add(like)
    db.commit()
    db.refresh(like)

    return like

def remove_like(db: Session, post_id: int, user_id: int) -> int:
    statement = (
        delete(Like).where(Like.post_id == post_id).where(Like.user_id == user_id)
    )
    result = db.execute(statement)
    db.commit()
    return result.rowcount

def get_like(db: Session, post_id: int, user_id: int) -> Like | None:
    statement = (
        select(Like)
        .where(Like.post_id == post_id)
        .where(Like.user_id == user_id)
    )

    return db.scalars(statement).first()

def get_likes(db: Session, post_id: int) -> list[Like]:

    statements = (
        select(Like)
        .options(selectinload(Like.user))
        .where(Like.post_id == post_id)
    )

    likes = list(db.scalars(statements).all())
    return likes

def count_likes(db: Session, post_id: int) -> int:
    statement = (
        select(func.count()).select_from(Like).where(Like.post_id == post_id)    
    )
    return db.scalar(statement) or 0

def is_liked_by_user(db: Session, post_id: int, user_id: int) -> bool:
    return get_like(db, post_id, user_id) is not None
