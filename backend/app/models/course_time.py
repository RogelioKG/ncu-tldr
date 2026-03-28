from sqlalchemy import ForeignKey, Index, Integer, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseTime(Base):
    __tablename__ = "course_times"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    period: Mapped[str] = mapped_column(Text, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="course_times")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        UniqueConstraint(
            "course_id", "day", "period", name="uq_course_times_cid_day_period"
        ),
        Index("idx_course_times_lookup", "day", "period"),
    )
