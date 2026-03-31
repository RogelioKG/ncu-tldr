import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WishVote(Base):
    __tablename__ = "wish_votes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    wish_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wishes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user: Mapped["User"] = relationship(back_populates="wish_votes")  # type: ignore[name-defined]  # noqa: F821
    wish: Mapped["Wish"] = relationship(back_populates="wish_votes")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (Index("idx_wish_votes_wish", "wish_id"),)
