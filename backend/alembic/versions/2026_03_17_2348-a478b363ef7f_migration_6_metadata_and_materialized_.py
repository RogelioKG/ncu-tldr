"""migration 6 metadata and materialized view

Revision ID: a478b363ef7f
Revises: a247ff1100bf
Create Date: 2026-03-17 23:48:15.418437

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a478b363ef7f"
down_revision: Union[str, Sequence[str], None] = "a247ff1100bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "metadata",
        sa.Column("id", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("last_update_time", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="single_row"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("metadata")
