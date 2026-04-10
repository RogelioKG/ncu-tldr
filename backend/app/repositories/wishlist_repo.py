import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wishlist import WishlistItem


class WishlistRepository:
    async def list_all(self, db: AsyncSession) -> list[WishlistItem]:
        result = await db.execute(
            select(WishlistItem).order_by(WishlistItem.vote_count.desc())
        )
        return list(result.scalars().all())

    async def create_or_upvote(
        self,
        db: AsyncSession,
        *,
        course_name: str,
        teacher_name: str,
        user_id: uuid.UUID,
    ) -> WishlistItem:
        stmt = (
            pg_insert(WishlistItem)
            .values(
                course_name=course_name,
                teacher_name=teacher_name,
                created_by=user_id,
                vote_count=1,
            )
            .on_conflict_do_update(
                constraint="uq_wishlist_course_teacher",
                set_={"vote_count": WishlistItem.__table__.c.vote_count + 1},
            )
            .returning(WishlistItem)
        )
        result = await db.execute(stmt)
        return result.scalars().one()

    async def delete(self, db: AsyncSession, wish_id: int) -> bool:
        item = await db.get(WishlistItem, wish_id)
        if item is None:
            return False
        await db.delete(item)
        await db.flush()
        return True


wishlist_repo = WishlistRepository()
