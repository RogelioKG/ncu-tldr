"""add email verification

Revision ID: 8bed4b506975
Revises: e8c3f72a1d09
Create Date: 2026-04-16 17:02:18.242347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8bed4b506975"
down_revision: Union[str, Sequence[str], None] = "e8c3f72a1d09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.create_table(
        "email_verification_tokens",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        "idx_evt_token", "email_verification_tokens", ["token"], unique=True
    )
    op.create_index("idx_evt_user_id", "email_verification_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_evt_user_id", table_name="email_verification_tokens")
    op.drop_index("idx_evt_token", table_name="email_verification_tokens")
    op.drop_table("email_verification_tokens")
    op.drop_column("users", "email_verified")
