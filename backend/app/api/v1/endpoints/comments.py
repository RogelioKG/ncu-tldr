from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.schemas.reaction import ReactionRequest, ReactionResponse
from app.schemas.review import CourseCommentOut
from app.services.comment_service import comment_service

router = APIRouter(tags=["comments"])


@router.get("/{course_id}/comments", response_model=list[CourseCommentOut])
async def list_comments(course_id: int, db: AsyncSession = Depends(get_db)):
    return await comment_service.list_comments(db, course_id)


@router.post("/{course_id}/comments", response_model=CourseCommentOut, status_code=201)
async def create_comment(
    course_id: int,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    return await comment_service.react_to_comment(db, comment_id, data.reaction)
