import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WishlistVote(Base):
    """One row = one user's vote for one course."""

    __tablename__ = "wishlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    course: Mapped["Course"] = relationship("Course")  # type: ignore[name-defined]  # noqa: F821
    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_wishlist_course_user"),
    )
