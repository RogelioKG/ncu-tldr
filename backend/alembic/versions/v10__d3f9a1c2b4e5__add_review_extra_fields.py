"""add semester weekly_hours textbook to reviews

Revision ID: d3f9a1c2b4e5
Revises: a4d56260b069
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f9a1c2b4e5'
down_revision: Union[str, Sequence[str], None] = 'a4d56260b069'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('reviews', sa.Column('semester', sa.Text(), nullable=True))
    op.add_column('reviews', sa.Column('weekly_hours', sa.SmallInteger(), nullable=True))
    op.add_column('reviews', sa.Column('textbook', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('reviews', 'textbook')
    op.drop_column('reviews', 'weekly_hours')
    op.drop_column('reviews', 'semester')
