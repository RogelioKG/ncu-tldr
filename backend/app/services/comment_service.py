from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.user import User
from app.repositories.comment_repo import comment_repo
from app.schemas.comment import CommentCreate
from app.schemas.reaction import ReactionResponse
from app.schemas.review import CourseCommentOut


def _comment_to_out(
    comment: Comment,
    current_user_id: str | None = None,
) -> CourseCommentOut:
    is_deleted = comment.is_deleted
    user_name = (
        "Anonymous"
        if is_deleted
        else (comment.user.display_name if comment.user else "Anonymous")
    )
    can_delete = (
        not is_deleted
        and current_user_id is not None
        and comment.user_id is not None
        and str(comment.user_id) == current_user_id
    )
    return CourseCommentOut(
        id=comment.id,
        user=user_name,
        title="",
        content="此留言已刪除" if is_deleted else comment.content,
        date=comment.created_at.isoformat(),
        likes=0 if is_deleted else comment.likes,
        dislikes=0 if is_deleted else comment.dislikes,
        parent_id=comment.parent_id,
        is_deleted=is_deleted,
        can_delete=can_delete,
        ratings=None,
    )


class CommentService:
    async def list_comments(
        self,
        db: AsyncSession,
        course_id: int,
        current_user: User | None,
    ) -> list[CourseCommentOut]:
        comments = await comment_repo.list_by_course(db, course_id)
        current_user_id = str(current_user.id) if current_user else None
        return [_comment_to_out(c, current_user_id) for c in comments]

    async def create_comment(
        self,
        db: AsyncSession,
        course_id: int,
        user: User,
        data: CommentCreate,
    ) -> CourseCommentOut:
        if data.parent_id is not None:
            parent = await comment_repo.get_active_by_id(
                db,
                course_id=course_id,
                comment_id=data.parent_id,
            )
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Comment {data.parent_id} not found",
                )

        comment = await comment_repo.create(
            db,
            course_id=course_id,
            user_id=user.id,
            parent_id=data.parent_id,
            content=data.content,
        )
        return _comment_to_out(comment, str(user.id))

    async def react_to_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        reaction: str,
    ) -> ReactionResponse:
        comment = await comment_repo.react(db, comment_id, reaction)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment {comment_id} not found",
            )
        return ReactionResponse(likes=comment.likes, dislikes=comment.dislikes)

    async def soft_delete_comment(
        self,
        db: AsyncSession,
        *,
        course_id: int,
        comment_id: int,
        user: User,
    ) -> None:
        deleted = await comment_repo.soft_delete(
            db,
            comment_id=comment_id,
            course_id=course_id,
            user_id=user.id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment {comment_id} not found",
            )


comment_service = CommentService()
