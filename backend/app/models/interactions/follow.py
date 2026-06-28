from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from datetime import datetime, timezone  

class Follow(Base):
    __tablename__ = "follows"

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follows_follower_following"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    follower: Mapped["User"] = relationship(
        foreign_keys=[follower_id],
        back_populates="following_relationships",
    )
    following: Mapped["User"] = relationship(
        foreign_keys=[following_id],
        back_populates="follower_relationships",
    )
