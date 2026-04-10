from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.wishlist import WishlistItem
from app.repositories.wishlist_repo import wishlist_repo
from app.schemas.wishlist import WishCourseOut, WishlistCreate


def _wish_to_out(item: WishlistItem) -> WishCourseOut:
    return WishCourseOut(
        id=item.id,
        name=item.course_name,
        teacher=item.teacher_name,
        vote_count=item.vote_count,
    )


class WishlistService:
    async def list_wishes(self, db: AsyncSession) -> list[WishCourseOut]:
        items = await wishlist_repo.list_all(db)
        return [_wish_to_out(i) for i in items]

    async def add_wish(
        self,
        db: AsyncSession,
        data: WishlistCreate,
        user: User | None,
    ) -> WishCourseOut:
        user_id = user.id if user is not None else None
        item = await wishlist_repo.create_or_upvote(
            db,
            course_name=data.name,
            teacher_name=data.teacher,
            user_id=user_id,
        )
        return _wish_to_out(item)

    async def delete_wish(
        self,
        db: AsyncSession,
        wish_id: int,
        user: User | None,
    ) -> None:
        deleted = await wishlist_repo.delete(db, wish_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Wish not found")


wishlist_service = WishlistService()
