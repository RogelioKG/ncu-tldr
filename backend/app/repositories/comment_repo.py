import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment


class CommentRepository:
    async def list_by_course(self, db: AsyncSession, course_id: int) -> list[Comment]:
        result = await db.execute(
            select(Comment)
            .where(Comment.course_id == course_id)
            .options(selectinload(Comment.user))
            .order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        user_id: uuid.UUID,
        parent_id: int | None,
        title: str | None,
        content: str,
    ) -> Comment:
        comment = Comment(
            course_id=course_id,
            user_id=user_id,
            parent_id=parent_id,
            title=title,
            content=content,
        )
        db.add(comment)
        await db.flush()
        await db.refresh(comment, attribute_names=["user"])
        return comment

    async def react(
        self, db: AsyncSession, comment_id: int, reaction: str
    ) -> Comment | None:
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        comment = result.scalar_one_or_none()
        if comment is None:
            return None
        if reaction == "like":
            comment.likes += 1
        else:
            comment.dislikes += 1
        await db.flush()
        return comment


comment_repo = CommentRepository()
