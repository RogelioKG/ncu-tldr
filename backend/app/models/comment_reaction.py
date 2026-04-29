import uuid

from sqlalchemy import Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

REACTION_ENUM = Enum("like", "dislike", name="reaction_type", create_type=False)


class CommentReaction(Base):
    __tablename__ = "comment_reactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True
    )
    reaction: Mapped[str] = mapped_column(REACTION_ENUM, nullable=False)

    __table_args__ = (Index("idx_comment_reactions_comment_id", "comment_id"),)
