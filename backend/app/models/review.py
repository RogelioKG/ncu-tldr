import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False, server_default=sa.text("''"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    gain: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    high_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    easiness: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    teacher_style: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=sa.text("0"))
    dislikes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=sa.text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", lazy="select")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        CheckConstraint("gain BETWEEN 1 AND 5", name="ck_reviews_gain"),
        CheckConstraint("high_score BETWEEN 1 AND 5", name="ck_reviews_high_score"),
        CheckConstraint("easiness BETWEEN 1 AND 5", name="ck_reviews_easiness"),
        CheckConstraint("teacher_style BETWEEN 1 AND 5", name="ck_reviews_teacher_style"),
        Index("idx_reviews_course_id", "course_id"),
        Index("idx_reviews_user_id", "user_id"),
    )
