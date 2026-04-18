import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    semester: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    gain: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    high_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    easiness: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    teacher_style: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    likes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=sa.text("0")
    )
    dislikes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=sa.text("0")
    )
    weekly_hours: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    textbook: Mapped[str | None] = mapped_column(Text, nullable=True)
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
        CheckConstraint("gain IS NULL OR gain BETWEEN 1 AND 5", name="ck_reviews_gain"),
        CheckConstraint(
            "high_score IS NULL OR high_score BETWEEN 1 AND 5",
            name="ck_reviews_high_score",
        ),
        CheckConstraint(
            "easiness IS NULL OR easiness BETWEEN 1 AND 5",
            name="ck_reviews_easiness",
        ),
        CheckConstraint(
            "teacher_style IS NULL OR teacher_style BETWEEN 1 AND 5",
            name="ck_reviews_teacher_style",
        ),
        Index("idx_reviews_course_id", "course_id"),
        Index("idx_reviews_user_id", "user_id"),
        Index("idx_reviews_course_id_is_deleted", "course_id", "is_deleted"),
    )
