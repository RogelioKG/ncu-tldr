import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Wish(Base):
    __tablename__ = "wishes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="SET NULL"),
    )
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    teacher: Mapped[str] = mapped_column(String(100), nullable=False)
    vote_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    creator: Mapped["User"] = relationship(back_populates="wishes")  # type: ignore[name-defined]  # noqa: F821
    course: Mapped["Course | None"] = relationship(back_populates="wishes")  # type: ignore[name-defined]  # noqa: F821
    wish_votes: Mapped[list["WishVote"]] = relationship(back_populates="wish")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        UniqueConstraint("course_name", "teacher", name="uq_wishes_name_teacher"),
        Index("idx_wishes_vote_count", vote_count.desc()),
        Index("idx_wishes_course_id", "course_id"),
    )
