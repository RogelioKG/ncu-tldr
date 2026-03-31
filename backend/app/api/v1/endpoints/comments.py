from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.models.comment import Comment
from app.models.course import Course
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter(prefix="/courses", tags=["comments"])


def _format_date(created_at) -> str:
    if created_at is None:
        return ""
    return created_at.strftime("%Y/%m/%d")


@router.get(
    "/{course_id}/comments",
    response_model=list[CommentOut],
)
async def get_comments(
    course_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[CommentOut]:
    result = await db.execute(
        select(Comment).where(Comment.course_id == course_id, Comment.is_deleted.is_(False)).order_by(Comment.created_at.desc()),
    )
    rows = result.scalars().all()
    return [
        CommentOut(
            id=c.id,
            user="匿名",
            title=c.title,
            content=c.content,
            date=_format_date(c.created_at),
            likes=c.likes,
            dislikes=c.dislikes,
            parentId=c.parent_id,
        )
        for c in rows
    ]


@router.post(
    "/{course_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    course_id: int,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
) -> CommentOut:
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="No user in database; create a user first (e.g. run seed).",
        )
    user_id: UUID = user.id
    if payload.parent_id is not None:
        parent = await db.get(Comment, payload.parent_id)
        if parent is None or parent.course_id != course_id:
            raise HTTPException(status_code=400, detail="Invalid parent_id")
    comment = Comment(
        course_id=course_id,
        user_id=user_id,
        parent_id=payload.parent_id,
        title=payload.title or payload.content[:50] if payload.content else None,
        content=payload.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentOut(
        id=comment.id,
        user="匿名",
        title=comment.title,
        content=comment.content,
        date=_format_date(comment.created_at),
        likes=comment.likes,
        dislikes=comment.dislikes,
        parentId=comment.parent_id,
    )
