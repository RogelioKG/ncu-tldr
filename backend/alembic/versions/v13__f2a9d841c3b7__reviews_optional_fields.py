"""reviews: semester required, content/ratings optional, fix title default

Revision ID: f2a9d841c3b7
Revises: 8bed4b506975
Create Date: 2026-04-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a9d841c3b7"
down_revision: Union[str, Sequence[str], None] = "8bed4b506975"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # backfill any existing NULL semesters before setting NOT NULL
    op.execute("UPDATE reviews SET semester = 'unknown' WHERE semester IS NULL")
    op.alter_column("reviews", "semester", nullable=False)

    # title no longer needs a server default (app always provides it)
    op.alter_column("reviews", "title", server_default=None)

    # content and rating fields become optional
    op.alter_column("reviews", "content", nullable=True)
    op.alter_column("reviews", "gain", nullable=True)
    op.alter_column("reviews", "high_score", nullable=True)
    op.alter_column("reviews", "easiness", nullable=True)
    op.alter_column("reviews", "teacher_style", nullable=True)

    # Update check constraints to allow NULL ratings
    op.drop_constraint("ck_reviews_gain", "reviews")
    op.drop_constraint("ck_reviews_high_score", "reviews")
    op.drop_constraint("ck_reviews_easiness", "reviews")
    op.drop_constraint("ck_reviews_teacher_style", "reviews")

    op.create_check_constraint(
        "ck_reviews_gain", "reviews", "gain IS NULL OR gain BETWEEN 1 AND 5"
    )
    op.create_check_constraint(
        "ck_reviews_high_score",
        "reviews",
        "high_score IS NULL OR high_score BETWEEN 1 AND 5",
    )
    op.create_check_constraint(
        "ck_reviews_easiness",
        "reviews",
        "easiness IS NULL OR easiness BETWEEN 1 AND 5",
    )
    op.create_check_constraint(
        "ck_reviews_teacher_style",
        "reviews",
        "teacher_style IS NULL OR teacher_style BETWEEN 1 AND 5",
    )


def downgrade() -> None:
    op.drop_constraint("ck_reviews_gain", "reviews")
    op.drop_constraint("ck_reviews_high_score", "reviews")
    op.drop_constraint("ck_reviews_easiness", "reviews")
    op.drop_constraint("ck_reviews_teacher_style", "reviews")

    op.create_check_constraint("ck_reviews_gain", "reviews", "gain BETWEEN 1 AND 5")
    op.create_check_constraint(
        "ck_reviews_high_score", "reviews", "high_score BETWEEN 1 AND 5"
    )
    op.create_check_constraint(
        "ck_reviews_easiness", "reviews", "easiness BETWEEN 1 AND 5"
    )
    op.create_check_constraint(
        "ck_reviews_teacher_style", "reviews", "teacher_style BETWEEN 1 AND 5"
    )

    op.alter_column("reviews", "title", server_default=sa.text("''"))
    op.alter_column("reviews", "semester", nullable=True)
    op.alter_column("reviews", "content", nullable=False)
    op.alter_column("reviews", "gain", nullable=False)
    op.alter_column("reviews", "high_score", nullable=False)
    op.alter_column("reviews", "easiness", nullable=False)
    op.alter_column("reviews", "teacher_style", nullable=False)
