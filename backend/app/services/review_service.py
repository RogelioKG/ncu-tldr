from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from app.repositories.course_repo import course_repo
from app.repositories.review_repo import review_repo
from app.schemas.reaction import ReactionResponse
from app.schemas.review import CourseCommentOut, MyReviewOut, RatingsOut, ReviewCreate


def _build_ratings(review: Review) -> RatingsOut | None:
    if not any(
        v is not None
        for v in [review.gain, review.high_score, review.easiness, review.teacher_style]
    ):
        return None
    return RatingsOut(
        gain=float(review.gain) if review.gain is not None else None,
        high_score=float(review.high_score) if review.high_score is not None else None,
        easiness=float(review.easiness) if review.easiness is not None else None,
        teacher_style=float(review.teacher_style)
        if review.teacher_style is not None
        else None,
    )


def _review_to_out(
    review: Review,
    current_user_id: str | None = None,
) -> CourseCommentOut:
    user_name = review.user.display_name if review.user else "Unknown"
    can_delete = (
        not review.is_deleted
        and current_user_id is not None
        and review.user_id is not None
        and str(review.user_id) == current_user_id
    )
    return CourseCommentOut(
        id=review.id,
        user=user_name,
        title=review.title,
        content=review.content,
        date=review.created_at.isoformat(),
        likes=review.likes,
        dislikes=review.dislikes,
        parent_id=None,
        is_deleted=review.is_deleted,
        can_delete=can_delete,
        ratings=_build_ratings(review),
        semester=review.semester,
        weekly_hours=review.weekly_hours,
        textbook=review.textbook,
    )


class ReviewService:
    async def list_reviews(
        self,
        db: AsyncSession,
        course_id: int,
        current_user: User | None,
    ) -> list[CourseCommentOut]:
        reviews = await review_repo.list_by_course(db, course_id)
        current_user_id = str(current_user.id) if current_user else None
        return [_review_to_out(r, current_user_id) for r in reviews]

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
        ratings = data.ratings
        review = await review_repo.create(
            db,
            course_id=course_id,
            user_id=user.id,
            semester=data.semester,
            title=data.title or f"[{data.semester}]",
            content=data.content,
            gain=ratings.gain or None if ratings else None,
            high_score=ratings.high_score or None if ratings else None,
            easiness=ratings.easiness or None if ratings else None,
            teacher_style=ratings.teacher_style or None if ratings else None,
            weekly_hours=data.weekly_hours,
            textbook=data.textbook,
        )
        return _review_to_out(review, str(user.id))

    async def list_my_reviews(self, db: AsyncSession, user: User) -> list[MyReviewOut]:
        rows = await review_repo.list_by_user(db, user.id)
        return [
            MyReviewOut(
                id=review.id,
                user=review.user.display_name if review.user else "Unknown",
                title=review.title,
                content=review.content,
                date=review.created_at.isoformat(),
                likes=review.likes,
                dislikes=review.dislikes,
                parent_id=None,
                is_deleted=review.is_deleted,
                can_delete=not review.is_deleted,
                ratings=_build_ratings(review),
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

    async def soft_delete_review(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        review_id: int,
        user: User,
    ) -> None:
        deleted = await review_repo.soft_delete(
            db,
            review_id=review_id,
            course_id=course_id,
            user_id=user.id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review {review_id} not found",
            )


review_service = ReviewService()
