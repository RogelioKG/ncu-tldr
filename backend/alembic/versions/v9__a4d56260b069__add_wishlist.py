"""add wishlist

Revision ID: a4d56260b069
Revises: bc192315260a
Create Date: 2026-04-10 10:15:13.935967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4d56260b069'
down_revision: Union[str, Sequence[str], None] = 'bc192315260a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "wishlist",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_name", sa.Text(), nullable=False),
        sa.Column("teacher_name", sa.Text(), nullable=False),
        sa.Column("vote_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_name", "teacher_name", name="uq_wishlist_course_teacher"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("wishlist")
