from sqlalchemy import ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseDepartment(Base):
    __tablename__ = "course_departments"

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        primary_key=True,
    )

    course: Mapped["Course"] = relationship(back_populates="course_departments")  # type: ignore[name-defined]  # noqa: F821
    department: Mapped["Department"] = relationship(back_populates="course_departments")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (Index("idx_cd_department_id", "department_id"),)
