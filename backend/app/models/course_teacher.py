import sqlalchemy as sa
from sqlalchemy import ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseTeacher(Base):
    __tablename__ = "course_teachers"

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sort_order: Mapped[int | None] = mapped_column(
        SmallInteger, server_default=sa.text("0")
    )

    course: Mapped["Course"] = relationship(back_populates="course_teachers")  # type: ignore[name-defined]  # noqa: F821
    teacher: Mapped["Teacher"] = relationship(back_populates="course_teachers")  # type: ignore[name-defined]  # noqa: F821
