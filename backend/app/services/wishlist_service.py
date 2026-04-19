import uuid
import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wishlist_repo import wishlist_repo
from app.schemas.wishlist import WishCourseOut

logger = logging.getLogger(__name__)


class WishlistService:
    async def list_wishes(
        self, db: AsyncSession, *, user_id: uuid.UUID | None
    ) -> list[WishCourseOut]:
        logger.debug("List wishlist service user_id=%s", user_id)
        return await wishlist_repo.list_courses_with_votes(db, user_id=user_id)

    async def add_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> None:
        logger.debug(
            "Add wishlist vote service course_id=%s user_id=%s", course_id, user_id
        )
        if not await wishlist_repo.course_exists(db, course_id):
            logger.warning(
                "Add wishlist vote failed: course not found course_id=%s", course_id
            )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
        already_voted = not await wishlist_repo.add_vote(
            db, course_id=course_id, user_id=user_id
        )
        if already_voted:
            logger.info(
                "Add wishlist vote conflict: already voted course_id=%s user_id=%s",
                course_id,
                user_id,
            )
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Already voted for this course"
            )
        logger.info(
            "Add wishlist vote succeeded course_id=%s user_id=%s", course_id, user_id
        )

    async def remove_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> None:
        logger.debug(
            "Remove wishlist vote service course_id=%s user_id=%s",
            course_id,
            user_id,
        )
        removed = await wishlist_repo.remove_vote(
            db, course_id=course_id, user_id=user_id
        )
        if not removed:
            logger.warning(
                "Remove wishlist vote failed: vote not found course_id=%s user_id=%s",
                course_id,
                user_id,
            )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vote not found")
        logger.info(
            "Remove wishlist vote succeeded course_id=%s user_id=%s", course_id, user_id
        )


wishlist_service = WishlistService()
