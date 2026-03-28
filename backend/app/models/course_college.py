from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseCollege(Base):
    __tablename__ = "course_colleges"

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    college_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("colleges.id", ondelete="CASCADE"),
        primary_key=True,
    )

    course: Mapped["Course"] = relationship(back_populates="course_colleges")  # type: ignore[name-defined]  # noqa: F821
    college: Mapped["College"] = relationship(back_populates="course_colleges")  # type: ignore[name-defined]  # noqa: F821
