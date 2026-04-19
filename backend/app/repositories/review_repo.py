import uuid
import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.review import Review

logger = logging.getLogger(__name__)


class ReviewRepository:
    async def list_by_course(self, db: AsyncSession, course_id: int) -> list[Review]:
        logger.debug("List reviews by course course_id=%s", course_id)
        result = await db.execute(
            select(Review)
            .where(Review.course_id == course_id, Review.is_deleted.is_(False))
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        user_id: uuid.UUID,
        semester: str,
        title: str = "",
        content: str | None = None,
        gain: int | None = None,
        high_score: int | None = None,
        easiness: int | None = None,
        teacher_style: int | None = None,
        weekly_hours: int | None = None,
        textbook: str | None = None,
    ) -> Review:
        review = Review(
            course_id=course_id,
            user_id=user_id,
            semester=semester,
            title=title,
            content=content,
            gain=gain,
            high_score=high_score,
            easiness=easiness,
            teacher_style=teacher_style,
            weekly_hours=weekly_hours,
            textbook=textbook,
        )
        db.add(review)
        await db.flush()
        await db.refresh(review, attribute_names=["user"])
        logger.info(
            "Review created review_id=%s course_id=%s user_id=%s",
            review.id,
            course_id,
            user_id,
        )
        return review

    async def list_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[tuple[Review, str]]:
        logger.debug("List reviews by user user_id=%s", user_id)
        result = await db.execute(
            select(Review, Course.title)
            .join(Course, Review.course_id == Course.id)
            .where(Review.user_id == user_id, Review.is_deleted.is_(False))
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
        )
        return [(row[0], row[1]) for row in result.all()]

    async def react(
        self, db: AsyncSession, review_id: int, reaction: str
    ) -> Review | None:
        logger.debug("React to review review_id=%s reaction=%s", review_id, reaction)
        result = await db.execute(
            select(Review).where(Review.id == review_id, Review.is_deleted.is_(False))
        )
        review = result.scalar_one_or_none()
        if review is None:
            logger.warning("React target review not found review_id=%s", review_id)
            return None
        if reaction == "like":
            review.likes += 1
        else:
            review.dislikes += 1
        await db.flush()
        logger.debug(
            "Review reaction updated review_id=%s likes=%s dislikes=%s",
            review.id,
            review.likes,
            review.dislikes,
        )
        return review

    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        review_id: int,
        course_id: int,
        user_id: uuid.UUID,
    ) -> bool:
        logger.debug(
            "Soft delete review requested review_id=%s course_id=%s user_id=%s",
            review_id,
            course_id,
            user_id,
        )
        result = await db.execute(
            select(Review).where(
                Review.id == review_id,
                Review.course_id == course_id,
                Review.user_id == user_id,
                Review.is_deleted.is_(False),
            )
        )
        review = result.scalar_one_or_none()
        if review is None:
            logger.warning(
                "Soft delete review target not found review_id=%s course_id=%s user_id=%s",
                review_id,
                course_id,
                user_id,
            )
            return False

        review.is_deleted = True
        review.deleted_at = datetime.now(UTC)
        review.deleted_by_user_id = user_id
        await db.flush()
        logger.info("Review soft deleted review_id=%s user_id=%s", review_id, user_id)
        return True


review_repo = ReviewRepository()
