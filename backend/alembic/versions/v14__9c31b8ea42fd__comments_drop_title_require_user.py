"""comments: drop title, require user_id, keep parent_id nullable

Revision ID: 9c31b8ea42fd
Revises: f2a9d841c3b7
Create Date: 2026-04-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9c31b8ea42fd"
down_revision: Union[str, Sequence[str], None] = "f2a9d841c3b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove historical rows that cannot satisfy the new NOT NULL constraint.
    op.execute("DELETE FROM comments WHERE user_id IS NULL")

    # Replace SET NULL behavior with CASCADE to match the non-null user_id.
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_user_id_fkey")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS fk_comments_user_id")
    op.create_foreign_key(
        "fk_comments_user_id",
        source_table="comments",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )

    op.alter_column("comments", "user_id", existing_type=sa.UUID(), nullable=False)
    op.drop_column("comments", "title")


def downgrade() -> None:
    op.add_column("comments", sa.Column("title", sa.Text(), nullable=True))

    op.alter_column("comments", "user_id", existing_type=sa.UUID(), nullable=True)
    op.drop_constraint("fk_comments_user_id", "comments", type_="foreignkey")
    op.create_foreign_key(
        "comments_user_id_fkey",
        source_table="comments",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )
