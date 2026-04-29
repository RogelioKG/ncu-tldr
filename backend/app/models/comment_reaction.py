import uuid

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommentReaction(Base):
    __tablename__ = "comment_reactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True
    )
    reaction: Mapped[str] = mapped_column(String(10), nullable=False)

    __table_args__ = (
        CheckConstraint(
            sa.text("reaction IN ('like', 'dislike')"),
            name="ck_comment_reactions_reaction",
        ),
        Index("idx_comment_reactions_comment_id", "comment_id"),
    )
