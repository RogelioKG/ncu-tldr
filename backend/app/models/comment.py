import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
    )
    title: Mapped[str | None] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    likes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    dislikes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    course: Mapped["Course"] = relationship(back_populates="comments")  # type: ignore[name-defined]  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="comments")  # type: ignore[name-defined]  # noqa: F821
    parent: Mapped["Comment | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        remote_side=[id],
        back_populates="replies",
    )
    replies: Mapped[list["Comment"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    comment_votes: Mapped[list["CommentVote"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_comments_course_id", "course_id", "created_at"),
        Index("idx_comments_user_id", "user_id"),
        Index("idx_comments_parent_id", "parent_id"),
    )
