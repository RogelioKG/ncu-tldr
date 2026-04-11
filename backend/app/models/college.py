import sqlalchemy as sa
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class College(Base):
    __tablename__ = "colleges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    departments: Mapped[list["Department"]] = relationship(back_populates="college")  # type: ignore[name-defined]  # noqa: F821
    course_colleges: Mapped[list["CourseCollege"]] = relationship(  # noqa: F821
        back_populates="college"
    )  # type: ignore[name-defined]

    __table_args__ = (sa.UniqueConstraint("code", name="uq_colleges_code"),)
