from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from app.repositories.review_repo import review_repo
from app.schemas.review import CourseCommentOut, RatingsOut, ReviewCreate


def _review_to_out(review: Review) -> CourseCommentOut:
    user_name = review.user.display_name if review.user else "Unknown"
    return CourseCommentOut(
        id=review.id,
        user=user_name,
        title=review.title or "",
        content=review.content,
        date=review.created_at.isoformat(),
        likes=review.likes,
        dislikes=review.dislikes,
        parent_id=None,
        ratings=RatingsOut(
            gain=float(review.gain),
            high_score=float(review.high_score),
            easiness=float(review.easiness),
            teacher_style=float(review.teacher_style),
        ),
    )


class ReviewService:
    async def list_reviews(
        self, db: AsyncSession, course_id: int
    ) -> list[CourseCommentOut]:
        reviews = await review_repo.list_by_course(db, course_id)
        return [_review_to_out(r) for r in reviews]

    async def create_review(
        self,
        db: AsyncSession,
        course_id: int,
        user: User,
        data: ReviewCreate,
    ) -> CourseCommentOut:
        review = await review_repo.create(
            db,
            course_id=course_id,
            user_id=user.id,
            title=data.title,
            content=data.content,
            gain=data.ratings.gain,
            high_score=data.ratings.high_score,
            easiness=data.ratings.easiness,
            teacher_style=data.ratings.teacher_style,
        )
        return _review_to_out(review)


review_service = ReviewService()
