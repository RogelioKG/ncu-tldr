from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.review import CourseCommentOut, ReviewCreate
from app.services.review_service import review_service

router = APIRouter(tags=["reviews"])


@router.get("/{course_id}/reviews", response_model=list[CourseCommentOut])
async def list_reviews(course_id: int, db: AsyncSession = Depends(get_db)):
    return await review_service.list_reviews(db, course_id)


@router.post("/{course_id}/reviews", response_model=CourseCommentOut, status_code=201)
async def create_review(
    course_id: int,
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await review_service.create_review(db, course_id, current_user, data)
