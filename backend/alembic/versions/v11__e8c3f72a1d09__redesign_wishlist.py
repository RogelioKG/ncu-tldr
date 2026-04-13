"""redesign wishlist: one row per user per course vote

Revision ID: e8c3f72a1d09
Revises: d3f9a1c2b4e5
Create Date: 2026-04-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8c3f72a1d09"
down_revision: Union[str, Sequence[str], None] = "d3f9a1c2b4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop old free-text wishlist and replace with per-user-per-course vote records."""
    op.drop_table("wishlist")

    op.create_table(
        "wishlist",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "user_id", name="uq_wishlist_course_user"),
    )
    op.create_index("idx_wishlist_course_id", "wishlist", ["course_id"], unique=False)
    op.create_index("idx_wishlist_user_id", "wishlist", ["user_id"], unique=False)


def downgrade() -> None:
    """Restore old free-text wishlist (data is lost)."""
    op.drop_index("idx_wishlist_user_id", table_name="wishlist")
    op.drop_index("idx_wishlist_course_id", table_name="wishlist")
    op.drop_table("wishlist")

    op.create_table(
        "wishlist",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_name", sa.Text(), nullable=False),
        sa.Column("teacher_name", sa.Text(), nullable=False),
        sa.Column(
            "vote_count", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_name", "teacher_name", name="uq_wishlist_course_teacher"
        ),
    )
