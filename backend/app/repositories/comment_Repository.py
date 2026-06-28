from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.interactions.comment import Comment


def create_comment(
    db: Session,
    post_id: int,
    user_id: int,
    content: str,
) -> Comment:
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_comments_by_post(db: Session, post_id: int) -> list[Comment]:
    statement = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )

    return list(db.scalars(statement).all())


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    statement = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment_id)
    )

    return db.scalars(statement).first()


def delete_comment(db: Session, comment_id: int, user_id: int) -> int:
    statement = (
        delete(Comment)
        .where(Comment.id == comment_id)
        .where(Comment.user_id == user_id)
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount


def count_comments(db: Session, post_id: int) -> int:
    statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.post_id == post_id)
    )

    return db.scalar(statement) or 0