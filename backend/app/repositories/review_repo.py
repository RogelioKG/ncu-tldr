import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
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
        semester: str | None = None,
        weekly_hours: int | None = None,
        textbook: str | None = None,
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
            semester=semester,
            weekly_hours=weekly_hours,
            textbook=textbook,
        )
        db.add(review)
        await db.flush()
        await db.refresh(review, attribute_names=["user"])
        return review


    async def list_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[tuple[Review, str]]:
        result = await db.execute(
            select(Review, Course.title)
            .join(Course, Review.course_id == Course.id)
            .where(Review.user_id == user_id)
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
        )
        return [(row[0], row[1]) for row in result.all()]

    async def react(self, db: AsyncSession, review_id: int, reaction: str) -> Review | None:
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one_or_none()
        if review is None:
            return None
        if reaction == "like":
            review.likes += 1
        else:
            review.dislikes += 1
        await db.flush()
        return review


review_repo = ReviewRepository()
