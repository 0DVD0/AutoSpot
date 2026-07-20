from app.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.userDTO import UserCreate, UserProfileUpdate
def get_user_by_id(db: Session, user_id: int) -> User | None:

    statement = select(User).where(User.id == user_id)
    user = db.scalars(statement).first()

    return user

def get_user_by_email(db: Session, user_email: str) -> User | None:
    statement = select(User).where(User.email == user_email)
    user = db.scalars(statement).first()
    return user

def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    user = db.scalars(statement).first()
    return user

def get_users(db: Session) -> list[User]:
    statements = select(User)
    users = list(db.scalars(statements).all())
    return users

def create_user(db: Session, user_data: UserCreate, hashed_pass: str) -> User:

    user = User(username = user_data.username, email = user_data.email, hashed_password = hashed_pass, avatar_url=str(user_data.avatar_url) if user_data.avatar_url else None, bio = user_data.bio)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def patch_user(db: Session, user: User, new_profile_data: UserProfileUpdate):
    update_data = new_profile_data.model_dump(exclude_unset=True)

    if "avatar_url" in update_data and update_data["avatar_url"] is not None:
        update_data["avatar_url"] = str(update_data["avatar_url"])
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user