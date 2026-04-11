"""add reviews and comments

Revision ID: bc192315260a
Revises: 06e06a2b41c3
Create Date: 2026-04-10 10:14:39.058631

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc192315260a"
down_revision: Union[str, Sequence[str], None] = "06e06a2b41c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("likes", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "dislikes", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_comments_course_id", "comments", ["course_id"], unique=False)
    op.create_index("idx_comments_parent_id", "comments", ["parent_id"], unique=False)
    op.create_index("idx_comments_user_id", "comments", ["user_id"], unique=False)
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("gain", sa.SmallInteger(), nullable=False),
        sa.Column("high_score", sa.SmallInteger(), nullable=False),
        sa.Column("easiness", sa.SmallInteger(), nullable=False),
        sa.Column("teacher_style", sa.SmallInteger(), nullable=False),
        sa.Column("likes", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "dislikes", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("easiness BETWEEN 1 AND 5", name="ck_reviews_easiness"),
        sa.CheckConstraint("gain BETWEEN 1 AND 5", name="ck_reviews_gain"),
        sa.CheckConstraint("high_score BETWEEN 1 AND 5", name="ck_reviews_high_score"),
        sa.CheckConstraint(
            "teacher_style BETWEEN 1 AND 5", name="ck_reviews_teacher_style"
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reviews_course_id", "reviews", ["course_id"], unique=False)
    op.create_index("idx_reviews_user_id", "reviews", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_reviews_user_id", table_name="reviews")
    op.drop_index("idx_reviews_course_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("idx_comments_user_id", table_name="comments")
    op.drop_index("idx_comments_parent_id", table_name="comments")
    op.drop_index("idx_comments_course_id", table_name="comments")
    op.drop_table("comments")
