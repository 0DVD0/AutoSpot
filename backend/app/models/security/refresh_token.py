from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, String, ForeignKey
from datetime import datetime, timezone
from uuid import uuid4
from app.models.base import Base

class RefreshToken(Base):
    __tablename__= "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default= lambda:str(uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE") ,index=True, nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)