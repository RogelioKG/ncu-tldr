"""add comment reactions

Revision ID: c4d5e6f7a1b2
Revises: a1b2c3d4e5f6
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7a1b2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "comment_reactions",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("reaction", sa.String(10), nullable=False),
        sa.CheckConstraint(
            "reaction IN ('like', 'dislike')",
            name="ck_comment_reactions_reaction",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "comment_id"),
    )
    op.create_index(
        "idx_comment_reactions_comment_id",
        "comment_reactions",
        ["comment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_comment_reactions_comment_id", table_name="comment_reactions")
    op.drop_table("comment_reactions")
