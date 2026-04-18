import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    likes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=sa.text("0")
    )
    dislikes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=sa.text("0")
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=sa.text("false")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User",
        lazy="select",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        Index("idx_comments_course_id", "course_id"),
        Index("idx_comments_parent_id", "parent_id"),
        Index("idx_comments_user_id", "user_id"),
        Index("idx_comments_course_id_is_deleted", "course_id", "is_deleted"),
    )
