import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.schemas.reaction import ReactionRequest, ReactionResponse
from app.schemas.review import CourseCommentOut
from app.services.comment_service import comment_service

router = APIRouter(tags=["comments"])
logger = logging.getLogger(__name__)


@router.get("/{course_id}/comments", response_model=list[CourseCommentOut])
async def list_comments(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    logger.debug("List comments endpoint course_id=%s", course_id)
    return await comment_service.list_comments(db, course_id, current_user)


@router.post("/{course_id}/comments", response_model=CourseCommentOut, status_code=201)
async def create_comment(
    course_id: int,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(
        "Create comment endpoint course_id=%s user_id=%s", course_id, current_user.id
    )
    return await comment_service.create_comment(db, course_id, current_user, data)


@router.post(
    "/{course_id}/comments/{comment_id}/react", response_model=ReactionResponse
)
async def react_to_comment(
    course_id: int,
    comment_id: int,
    data: ReactionRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.debug(
        "React comment endpoint course_id=%s comment_id=%s", course_id, comment_id
    )
    return await comment_service.react_to_comment(db, comment_id, data.reaction)


@router.delete(
    "/{course_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    course_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(
        "Delete comment endpoint course_id=%s comment_id=%s user_id=%s",
        course_id,
        comment_id,
        current_user.id,
    )
    await comment_service.soft_delete_comment(
        db,
        course_id=course_id,
        comment_id=comment_id,
        user=current_user,
    )
