from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    college_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
    )

    college: Mapped["College"] = relationship(back_populates="departments")  # type: ignore[name-defined]  # noqa: F821
    course_departments: Mapped[list["CourseDepartment"]] = relationship(  # noqa: F821
        back_populates="department"
    )  # type: ignore[name-defined]

    __table_args__ = (
        UniqueConstraint("code", name="uq_departments_code"),
        UniqueConstraint("name", name="uq_departments_name"),
        Index("idx_departments_college_id", "college_id"),
    )
