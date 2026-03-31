import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    guide_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    credibility_score: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, server_default=text("1.0"))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    total_reviews: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_comments: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    wishes: Mapped[list["Wish"]] = relationship(back_populates="creator")  # type: ignore[name-defined]  # noqa: F821
    wish_votes: Mapped[list["WishVote"]] = relationship(back_populates="user")  # type: ignore[name-defined]  # noqa: F821
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")  # type: ignore[name-defined]  # noqa: F821
    comment_votes: Mapped[list["CommentVote"]] = relationship(back_populates="user")  # type: ignore[name-defined]  # noqa: F821

    __table_args__ = (
        CheckConstraint(
            "credibility_score BETWEEN 0.1 AND 5.0",
            name="ck_users_credibility_range",
        ),
    )
