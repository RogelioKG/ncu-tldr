"""migration 5 indexes concurrently

Revision ID: a247ff1100bf
Revises: e2f220a299e5
Create Date: 2026-03-17 23:48:14.780685

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a247ff1100bf"
down_revision: Union[str, Sequence[str], None] = "e2f220a299e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.get_context().autocommit_block():
        op.create_index(
            "idx_departments_college_id",
            "departments",
            ["college_id"],
            unique=False,
            postgresql_concurrently=True,
        )
        op.create_index(
            "idx_cd_department_id",
            "course_departments",
            ["department_id"],
            unique=False,
            postgresql_concurrently=True,
        )
        op.create_index(
            "idx_teacher_name",
            "teachers",
            ["name"],
            unique=False,
            postgresql_concurrently=True,
        )
        op.create_index(
            "idx_course_times_lookup",
            "course_times",
            ["day", "period"],
            unique=False,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.get_context().autocommit_block():
        op.drop_index(
            "idx_course_times_lookup",
            table_name="course_times",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "idx_teacher_name",
            table_name="teachers",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "idx_cd_department_id",
            table_name="course_departments",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "idx_departments_college_id",
            table_name="departments",
            postgresql_concurrently=True,
        )
