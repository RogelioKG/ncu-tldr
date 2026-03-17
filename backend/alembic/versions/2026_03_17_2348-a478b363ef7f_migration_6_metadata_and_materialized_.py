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
        sa.Column("last_update_time", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="single_row"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW course_search_view AS
        SELECT
            c.serial_no,
            c.title,
            array_agg(DISTINCT t.name) AS teachers
        FROM courses c
        LEFT JOIN course_teachers ct ON c.serial_no = ct.course_id
        LEFT JOIN teachers t ON ct.teacher_id = t.id
        GROUP BY c.serial_no, c.title
        """
    )

    # Required for `REFRESH MATERIALIZED VIEW CONCURRENTLY course_search_view`
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE UNIQUE INDEX CONCURRENTLY uq_course_search_view_serial_no ON course_search_view(serial_no)"
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS uq_course_search_view_serial_no")

    op.execute("DROP MATERIALIZED VIEW IF EXISTS course_search_view")
    op.drop_table("metadata")
