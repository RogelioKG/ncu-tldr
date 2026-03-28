from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

course_type_enum = ENUM(
    "REQUIRED", "ELECTIVE", name="course_type_enum", create_type=False
)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_no: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    credit: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    password_card: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'NONE'")
    )
    limit_cnt: Mapped[int | None] = mapped_column(Integer)
    admit_cnt: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    wait_cnt: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    course_type: Mapped[str] = mapped_column(course_type_enum, nullable=False)
    last_semester: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    course_teachers: Mapped[list["CourseTeacher"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )
    course_times: Mapped[list["CourseTime"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )
    course_departments: Mapped[list["CourseDepartment"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )
    course_colleges: Mapped[list["CourseCollege"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("external_id", name="uq_courses_external_id"),
        UniqueConstraint("class_no"),
        CheckConstraint("credit >= 0", name="ck_courses_credit_nonnegative"),
    )
