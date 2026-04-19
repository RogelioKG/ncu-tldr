import uuid
import logging

from sqlalchemy import func, literal, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.wishlist import WishlistVote
from app.schemas.wishlist import WishCourseOut

logger = logging.getLogger(__name__)


class WishlistRepository:
    async def list_courses_with_votes(
        self, db: AsyncSession, *, user_id: uuid.UUID | None
    ) -> list[WishCourseOut]:
        logger.debug("List wishlist courses with votes user_id=%s", user_id)
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
        logger.debug("Add wishlist vote course_id=%s user_id=%s", course_id, user_id)
        stmt = (
            pg_insert(WishlistVote)
            .values(course_id=course_id, user_id=user_id)
            .on_conflict_do_nothing(constraint="uq_wishlist_course_user")
            .returning(WishlistVote.id)
        )
        result = await db.execute(stmt)
        inserted = result.scalar_one_or_none() is not None
        if inserted:
            logger.info(
                "Wishlist vote added course_id=%s user_id=%s", course_id, user_id
            )
        else:
            logger.warning(
                "Wishlist duplicate vote blocked course_id=%s user_id=%s",
                course_id,
                user_id,
            )
        return inserted

    async def remove_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> bool:
        """Delete the user's vote. Returns False if no vote existed."""
        logger.debug("Remove wishlist vote course_id=%s user_id=%s", course_id, user_id)
        vote = await db.scalar(
            select(WishlistVote).where(
                WishlistVote.course_id == course_id,
                WishlistVote.user_id == user_id,
            )
        )
        if vote is None:
            logger.warning(
                "Wishlist vote not found course_id=%s user_id=%s", course_id, user_id
            )
            return False
        await db.delete(vote)
        await db.flush()
        logger.info("Wishlist vote removed course_id=%s user_id=%s", course_id, user_id)
        return True

    async def course_exists(self, db: AsyncSession, course_id: int) -> bool:
        logger.debug("Check course exists for wishlist course_id=%s", course_id)
        result = await db.scalar(select(Course.id).where(Course.id == course_id))
        return result is not None


wishlist_repo = WishlistRepository()
