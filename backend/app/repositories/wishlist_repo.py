import uuid

from sqlalchemy import func, literal, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.wishlist import WishlistVote
from app.schemas.wishlist import WishCourseOut


class WishlistRepository:
    async def list_courses_with_votes(
        self, db: AsyncSession, *, user_id: uuid.UUID | None
    ) -> list[WishCourseOut]:
        has_voted_expr = (
            func.bool_or(WishlistVote.user_id == user_id)
            if user_id is not None
            else literal(False)
        )
        stmt = (
            select(
                Course.id.label("course_id"),
                Course.title,
                func.count(WishlistVote.id).label("vote_count"),
                has_voted_expr.label("has_voted"),
            )
            .join(Course, Course.id == WishlistVote.course_id)
            .group_by(Course.id)
            .order_by(func.count(WishlistVote.id).desc())
        )
        result = await db.execute(stmt)
        return [WishCourseOut.model_validate(dict(row)) for row in result.mappings()]

    async def add_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> bool:
        """Insert a vote. Returns False if the user already voted for this course."""
        stmt = (
            pg_insert(WishlistVote)
            .values(course_id=course_id, user_id=user_id)
            .on_conflict_do_nothing(constraint="uq_wishlist_course_user")
            .returning(WishlistVote.id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def remove_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> bool:
        """Delete the user's vote. Returns False if no vote existed."""
        vote = await db.scalar(
            select(WishlistVote).where(
                WishlistVote.course_id == course_id,
                WishlistVote.user_id == user_id,
            )
        )
        if vote is None:
            return False
        await db.delete(vote)
        await db.flush()
        return True

    async def course_exists(self, db: AsyncSession, course_id: int) -> bool:
        result = await db.scalar(select(Course.id).where(Course.id == course_id))
        return result is not None


wishlist_repo = WishlistRepository()
