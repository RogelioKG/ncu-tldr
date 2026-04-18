"""add soft delete fields for reviews/comments

Revision ID: 1a2b3c4d5e6f
Revises: 5dc0a0a89f21
Create Date: 2026-04-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, Sequence[str], None] = "5dc0a0a89f21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reviews",
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )
    op.add_column(
        "reviews",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "reviews",
        sa.Column("deleted_by_user_id", sa.UUID(), nullable=True),
    )

    op.create_index(
        "idx_reviews_course_id_is_deleted",
        "reviews",
        ["course_id", "is_deleted"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_reviews_deleted_by_user_id",
        source_table="reviews",
        referent_table="users",
        local_cols=["deleted_by_user_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )

    op.execute("ALTER TABLE reviews DROP CONSTRAINT IF EXISTS reviews_user_id_fkey")
    op.execute("ALTER TABLE reviews DROP CONSTRAINT IF EXISTS fk_reviews_user_id")
    op.alter_column("reviews", "user_id", existing_type=sa.UUID(), nullable=True)
    op.create_foreign_key(
        "fk_reviews_user_id",
        source_table="reviews",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "comments",
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )
    op.add_column(
        "comments",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "comments",
        sa.Column("deleted_by_user_id", sa.UUID(), nullable=True),
    )

    op.create_index(
        "idx_comments_course_id_is_deleted",
        "comments",
        ["course_id", "is_deleted"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_comments_deleted_by_user_id",
        source_table="comments",
        referent_table="users",
        local_cols=["deleted_by_user_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )

    op.alter_column("reviews", "is_deleted", server_default=None)
    op.alter_column("comments", "is_deleted", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_comments_deleted_by_user_id", "comments", type_="foreignkey")
    op.drop_index("idx_comments_course_id_is_deleted", table_name="comments")
    op.drop_column("comments", "deleted_by_user_id")
    op.drop_column("comments", "deleted_at")
    op.drop_column("comments", "is_deleted")

    op.drop_constraint("fk_reviews_deleted_by_user_id", "reviews", type_="foreignkey")
    op.drop_index("idx_reviews_course_id_is_deleted", table_name="reviews")
    op.drop_column("reviews", "deleted_by_user_id")
    op.drop_column("reviews", "deleted_at")
    op.drop_column("reviews", "is_deleted")

    op.execute("DELETE FROM reviews WHERE user_id IS NULL")
    op.execute("ALTER TABLE reviews DROP CONSTRAINT IF EXISTS reviews_user_id_fkey")
    op.execute("ALTER TABLE reviews DROP CONSTRAINT IF EXISTS fk_reviews_user_id")
    op.alter_column("reviews", "user_id", existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key(
        "reviews_user_id_fkey",
        source_table="reviews",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
