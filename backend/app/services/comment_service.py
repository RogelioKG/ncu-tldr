from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.user import User
from app.repositories.comment_repo import comment_repo
from app.schemas.comment import CommentCreate
from app.schemas.reaction import ReactionResponse
from app.schemas.review import CourseCommentOut


def _comment_to_out(comment: Comment) -> CourseCommentOut:
    user_name = comment.user.display_name if comment.user else "Anonymous"
    return CourseCommentOut(
        id=comment.id,
        user=user_name,
        title=comment.title or "",
        content=comment.content,
        date=comment.created_at.isoformat(),
        likes=comment.likes,
        dislikes=comment.dislikes,
        parent_id=comment.parent_id,
        ratings=None,
    )


class CommentService:
    async def list_comments(
        self, db: AsyncSession, course_id: int
    ) -> list[CourseCommentOut]:
        comments = await comment_repo.list_by_course(db, course_id)
        return [_comment_to_out(c) for c in comments]

    async def create_comment(
        self,
        db: AsyncSession,
        course_id: int,
        user: User,
        data: CommentCreate,
    ) -> CourseCommentOut:
        comment = await comment_repo.create(
            db,
            course_id=course_id,
            user_id=user.id,
            parent_id=data.parent_id,
            title=data.title,
            content=data.content,
        )
        return _comment_to_out(comment)

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


comment_service = CommentService()
