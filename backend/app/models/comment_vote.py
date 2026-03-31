import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CommentVote(Base):
    __tablename__ = "comment_votes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    vote_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user: Mapped["User"] = relationship(back_populates="comment_votes")  # type: ignore[name-defined]  # noqa: F821
    comment: Mapped["Comment"] = relationship(back_populates="comment_votes")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        CheckConstraint("vote_type IN (1, -1)", name="ck_comment_votes_vote_type"),
        Index("idx_comment_votes_comment", "comment_id"),
    )
