from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from app.repositories.course_repo import course_repo
from app.repositories.review_repo import review_repo
from app.schemas.reaction import ReactionResponse
from app.schemas.review import CourseCommentOut, MyReviewOut, RatingsOut, ReviewCreate


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
        semester=review.semester,
        weekly_hours=review.weekly_hours,
        textbook=review.textbook,
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
        course = await course_repo.get_by_id(db, course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found",
            )
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
            semester=data.semester,
            weekly_hours=data.weekly_hours,
            textbook=data.textbook,
        )
        return _review_to_out(review)

    async def list_my_reviews(self, db: AsyncSession, user: User) -> list[MyReviewOut]:
        rows = await review_repo.list_by_user(db, user.id)
        return [
            MyReviewOut(
                id=review.id,
                user=review.user.display_name if review.user else "Unknown",
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
                semester=review.semester,
                weekly_hours=review.weekly_hours,
                textbook=review.textbook,
                course_name=course_title,
                course_id=review.course_id,
            )
            for review, course_title in rows
        ]

    async def react_to_review(
        self,
        db: AsyncSession,
        review_id: int,
        reaction: str,
    ) -> ReactionResponse:
        review = await review_repo.react(db, review_id, reaction)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review {review_id} not found",
            )
        return ReactionResponse(likes=review.likes, dislikes=review.dislikes)


review_service = ReviewService()
