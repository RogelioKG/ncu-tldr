import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wishlist_repo import wishlist_repo
from app.schemas.wishlist import WishCourseOut


class WishlistService:
    async def list_wishes(
        self, db: AsyncSession, *, user_id: uuid.UUID | None
    ) -> list[WishCourseOut]:
        return await wishlist_repo.list_courses_with_votes(db, user_id=user_id)

    async def add_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> None:
        if not await wishlist_repo.course_exists(db, course_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
        already_voted = not await wishlist_repo.add_vote(
            db, course_id=course_id, user_id=user_id
        )
        if already_voted:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Already voted for this course"
            )

    async def remove_vote(
        self, db: AsyncSession, *, course_id: int, user_id: uuid.UUID
    ) -> None:
        removed = await wishlist_repo.remove_vote(
            db, course_id=course_id, user_id=user_id
        )
        if not removed:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vote not found")


wishlist_service = WishlistService()
