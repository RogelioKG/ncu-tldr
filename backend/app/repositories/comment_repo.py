import uuid
import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.comment_reaction import CommentReaction

logger = logging.getLogger(__name__)


class CommentRepository:
    async def list_by_course(self, db: AsyncSession, course_id: int) -> list[Comment]:
        logger.debug("List comments by course course_id=%s", course_id)
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
        logger.info(
            "Comment created comment_id=%s course_id=%s user_id=%s parent_id=%s",
            comment.id,
            course_id,
            user_id,
            parent_id,
        )
        return comment

    async def react(
        self,
        db: AsyncSession,
        *,
        comment_id: int,
        user_id: uuid.UUID,
        reaction: str,
    ) -> tuple[Comment, str | None] | None:
        logger.debug(
            "React to comment comment_id=%s user_id=%s reaction=%s",
            comment_id,
            user_id,
            reaction,
        )
        result = await db.execute(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.is_deleted.is_(False),
            )
        )
        comment = result.scalar_one_or_none()
        if comment is None:
            logger.warning("React target comment not found comment_id=%s", comment_id)
            return None

        existing_result = await db.execute(
            select(CommentReaction).where(
                CommentReaction.user_id == user_id,
                CommentReaction.comment_id == comment_id,
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing is not None:
            if existing.reaction == reaction:
                await db.delete(existing)
                if reaction == "like":
                    comment.likes = max(0, comment.likes - 1)
                else:
                    comment.dislikes = max(0, comment.dislikes - 1)
                user_reaction = None
            else:
                if reaction == "like":
                    comment.likes += 1
                    comment.dislikes = max(0, comment.dislikes - 1)
                else:
                    comment.dislikes += 1
                    comment.likes = max(0, comment.likes - 1)
                existing.reaction = reaction
                user_reaction = reaction
        else:
            db.add(
                CommentReaction(
                    user_id=user_id, comment_id=comment_id, reaction=reaction
                )
            )
            if reaction == "like":
                comment.likes += 1
            else:
                comment.dislikes += 1
            user_reaction = reaction

        await db.flush()
        logger.debug(
            "Comment reaction updated comment_id=%s likes=%s dislikes=%s user_reaction=%s",
            comment.id,
            comment.likes,
            comment.dislikes,
            user_reaction,
        )
        return comment, user_reaction

    async def get_user_reactions(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        comment_ids: list[int],
    ) -> dict[int, str]:
        if not comment_ids:
            return {}
        result = await db.execute(
            select(CommentReaction).where(
                CommentReaction.user_id == user_id,
                CommentReaction.comment_id.in_(comment_ids),
            )
        )
        return {r.comment_id: r.reaction for r in result.scalars().all()}

    async def get_active_by_id(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        comment_id: int,
    ) -> Comment | None:
        logger.debug(
            "Get active comment course_id=%s comment_id=%s", course_id, comment_id
        )
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
        logger.debug(
            "Soft delete comment requested comment_id=%s course_id=%s user_id=%s",
            comment_id,
            course_id,
            user_id,
        )
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
            logger.warning(
                "Soft delete comment target not found comment_id=%s course_id=%s user_id=%s",
                comment_id,
                course_id,
                user_id,
            )
            return False

        comment.is_deleted = True
        comment.deleted_at = datetime.now(UTC)
        comment.deleted_by_user_id = user_id
        await db.flush()
        logger.info(
            "Comment soft deleted comment_id=%s user_id=%s", comment_id, user_id
        )
        return True


comment_repo = CommentRepository()
