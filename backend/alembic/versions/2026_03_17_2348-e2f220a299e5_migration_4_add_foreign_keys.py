"""migration 4 add foreign keys

Revision ID: e2f220a299e5
Revises: 353b43253264
Create Date: 2026-03-17 23:48:14.161462

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e2f220a299e5"
down_revision: Union[str, Sequence[str], None] = "353b43253264"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        "fk_dept_college",
        source_table="departments",
        referent_table="colleges",
        local_cols=["college_id"],
        remote_cols=["id"],
    )

    op.create_foreign_key(
        "fk_ct_course",
        source_table="course_teachers",
        referent_table="courses",
        local_cols=["course_id"],
        remote_cols=["serial_no"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_ct_teacher",
        source_table="course_teachers",
        referent_table="teachers",
        local_cols=["teacher_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_ctime_course",
        source_table="course_times",
        referent_table="courses",
        local_cols=["course_id"],
        remote_cols=["serial_no"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_cd_course",
        source_table="course_departments",
        referent_table="courses",
        local_cols=["course_id"],
        remote_cols=["serial_no"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_cd_dept",
        source_table="course_departments",
        referent_table="departments",
        local_cols=["department_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_cd_dept", "course_departments", type_="foreignkey")
    op.drop_constraint("fk_cd_course", "course_departments", type_="foreignkey")
    op.drop_constraint("fk_ctime_course", "course_times", type_="foreignkey")
    op.drop_constraint("fk_ct_teacher", "course_teachers", type_="foreignkey")
    op.drop_constraint("fk_ct_course", "course_teachers", type_="foreignkey")
    op.drop_constraint("fk_dept_college", "departments", type_="foreignkey")
