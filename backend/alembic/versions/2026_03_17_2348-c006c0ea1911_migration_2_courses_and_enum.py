"""migration 2 courses and enum

Revision ID: c006c0ea1911
Revises: 50b6a42940f4
Create Date: 2026-03-17 23:48:12.873755

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c006c0ea1911"
down_revision: Union[str, Sequence[str], None] = "50b6a42940f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'course_type_enum') THEN
            CREATE TYPE course_type_enum AS ENUM ('REQUIRED', 'ELECTIVE');
          END IF;
        END$$;
        """
    )

    course_type_enum = postgresql.ENUM(
        "REQUIRED",
        "ELECTIVE",
        name="course_type_enum",
        create_type=False,
    )

    op.create_table(
        "courses",
        sa.Column("serial_no", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("class_no", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("credit", sa.SmallInteger(), nullable=False),
        sa.Column(
            "password_card",
            sa.Text(),
            server_default=sa.text("'NONE'"),
            nullable=False,
        ),
        sa.Column(
            "limit_cnt", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "admit_cnt", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "wait_cnt", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("course_type", course_type_enum, nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("credit > 0", name="ck_courses_credit_positive"),
        sa.PrimaryKeyConstraint("serial_no"),
        sa.UniqueConstraint("class_no"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("courses")
    op.execute("DROP TYPE IF EXISTS course_type_enum;")
