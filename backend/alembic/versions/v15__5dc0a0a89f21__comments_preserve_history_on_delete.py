"""comments: preserve history on user/parent delete

Revision ID: 5dc0a0a89f21
Revises: 9c31b8ea42fd
Create Date: 2026-04-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5dc0a0a89f21"
down_revision: Union[str, Sequence[str], None] = "9c31b8ea42fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("comments", "user_id", existing_type=sa.UUID(), nullable=True)

    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_user_id_fkey")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS fk_comments_user_id")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_parent_id_fkey")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS fk_comments_parent_id")

    op.create_foreign_key(
        "fk_comments_user_id",
        source_table="comments",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_comments_parent_id",
        source_table="comments",
        referent_table="comments",
        local_cols=["parent_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.execute("DELETE FROM comments WHERE user_id IS NULL")

    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_user_id_fkey")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS fk_comments_user_id")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_parent_id_fkey")
    op.execute("ALTER TABLE comments DROP CONSTRAINT IF EXISTS fk_comments_parent_id")

    op.create_foreign_key(
        "fk_comments_user_id",
        source_table="comments",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_comments_parent_id",
        source_table="comments",
        referent_table="comments",
        local_cols=["parent_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )

    op.alter_column("comments", "user_id", existing_type=sa.UUID(), nullable=False)
