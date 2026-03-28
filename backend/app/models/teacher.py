from sqlalchemy import Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    course_teachers: Mapped[list["CourseTeacher"]] = relationship(  # noqa: F821
        back_populates="teacher"
    )  # type: ignore[name-defined]

    __table_args__ = (Index("idx_teacher_name", "name"),)
