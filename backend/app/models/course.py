from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    course_code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    course_type: Mapped[str] = mapped_column(String(20), nullable=False)
    schedule: Mapped[str | None] = mapped_column(String(100))
    last_offered_semester: Mapped[str | None] = mapped_column(String(20))
    avg_reward: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False, server_default=text("0")
    )
    avg_score: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False, server_default=text("0")
    )
    avg_easiness: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False, server_default=text("0")
    )
    avg_teacher_style: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False, server_default=text("0")
    )
    avg_overall: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False, server_default=text("0")
    )
    review_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    department: Mapped["Department"] = relationship(back_populates="courses")  # type: ignore[name-defined]  # noqa: F821
    teacher: Mapped["Teacher"] = relationship(back_populates="courses")  # type: ignore[name-defined]  # noqa: F821
    wishes: Mapped[list["Wish"]] = relationship(back_populates="course")  # type: ignore[name-defined]  # noqa: F821
    comments: Mapped[list["Comment"]] = relationship(back_populates="course")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        UniqueConstraint("course_code", "teacher_id", name="uq_courses_code_teacher"),
        Index("idx_courses_department", "department_id"),
        Index("idx_courses_teacher", "teacher_id"),
        Index("idx_courses_name", "name"),
        Index("idx_courses_avg_overall", avg_overall.desc()),
    )
