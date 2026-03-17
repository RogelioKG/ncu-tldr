"""migration 3 relation tables no fk

Revision ID: 353b43253264
Revises: c006c0ea1911
Create Date: 2026-03-17 23:48:13.510440

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "353b43253264"
down_revision: Union[str, Sequence[str], None] = "c006c0ea1911"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "course_teachers",
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("teacher_id", sa.Integer(), nullable=True),
        sa.Column(
            "sort_order", sa.SmallInteger(), server_default=sa.text("0"), nullable=True
        ),
        sa.PrimaryKeyConstraint("course_id", "teacher_id"),
    )

    op.create_table(
        "course_times",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("day", sa.SmallInteger(), nullable=True),
        sa.Column("period", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "course_departments",
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("course_id", "department_id"),
    )

    op.create_table(
        "course_colleges",
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("college_id", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("course_id", "college_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("course_colleges")
    op.drop_table("course_departments")
    op.drop_table("course_times")
    op.drop_table("course_teachers")
