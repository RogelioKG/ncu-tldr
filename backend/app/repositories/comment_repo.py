import uuid
from datetime import UTC, datetime

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
        content: str,
    ) -> Comment:
        comment = Comment(
            course_id=course_id,
            user_id=user_id,
            parent_id=parent_id,
            content=content,
        )
        db.add(comment)
        await db.flush()
        await db.refresh(comment, attribute_names=["user"])
        return comment

    async def react(
        self, db: AsyncSession, comment_id: int, reaction: str
    ) -> Comment | None:
        result = await db.execute(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.is_deleted.is_(False),
            )
        )
        comment = result.scalar_one_or_none()
        if comment is None:
            return None
        if reaction == "like":
            comment.likes += 1
        else:
            comment.dislikes += 1
        await db.flush()
        return comment

    async def get_active_by_id(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        comment_id: int,
    ) -> Comment | None:
        result = await db.execute(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.course_id == course_id,
                Comment.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        comment_id: int,
        course_id: int,
        user_id: uuid.UUID,
    ) -> bool:
        result = await db.execute(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.course_id == course_id,
                Comment.user_id == user_id,
                Comment.is_deleted.is_(False),
            )
        )
        comment = result.scalar_one_or_none()
        if comment is None:
            return False

        comment.is_deleted = True
        comment.deleted_at = datetime.now(UTC)
        comment.deleted_by_user_id = user_id
        await db.flush()
        return True


comment_repo = CommentRepository()
