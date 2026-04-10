import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review


class ReviewRepository:
    async def list_by_course(self, db: AsyncSession, course_id: int) -> list[Review]:
        result = await db.execute(
            select(Review)
            .where(Review.course_id == course_id)
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
        title: str,
        content: str,
        gain: int,
        high_score: int,
        easiness: int,
        teacher_style: int,
    ) -> Review:
        review = Review(
            course_id=course_id,
            user_id=user_id,
            title=title,
            content=content,
            gain=gain,
            high_score=high_score,
            easiness=easiness,
            teacher_style=teacher_style,
        )
        db.add(review)
        await db.flush()
        await db.refresh(review, attribute_names=["user"])
        return review


review_repo = ReviewRepository()
