import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.reaction import ReactionRequest, ReactionResponse
from app.schemas.review import CourseCommentOut, ReviewCreate
from app.services.review_service import review_service

router = APIRouter(tags=["reviews"])
logger = logging.getLogger(__name__)


@router.get("/{course_id}/reviews", response_model=list[CourseCommentOut])
async def list_reviews(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    logger.debug("List reviews endpoint course_id=%s", course_id)
    return await review_service.list_reviews(db, course_id, current_user)


@router.post("/{course_id}/reviews", response_model=CourseCommentOut, status_code=201)
async def create_review(
    course_id: int,
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(
        "Create review endpoint course_id=%s user_id=%s", course_id, current_user.id
    )
    return await review_service.create_review(db, course_id, current_user, data)


@router.post("/{course_id}/reviews/{review_id}/react", response_model=ReactionResponse)
async def react_to_review(
    course_id: int,
    review_id: int,
    data: ReactionRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.debug(
        "React review endpoint course_id=%s review_id=%s", course_id, review_id
    )
    return await review_service.react_to_review(db, review_id, data.reaction)


@router.delete(
    "/{course_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_review(
    course_id: int,
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(
        "Delete review endpoint course_id=%s review_id=%s user_id=%s",
        course_id,
        review_id,
        current_user.id,
    )
    await review_service.soft_delete_review(
        db,
        course_id=course_id,
        review_id=review_id,
        user=current_user,
    )
