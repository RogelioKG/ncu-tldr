import uuid

from sqlalchemy import select
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
        result = await db.execute(
            select(WishlistItem)
            .where(WishlistItem.course_name == course_name)
            .where(WishlistItem.teacher_name == teacher_name)
        )
        existing = result.scalars().first()
        if existing:
            existing.vote_count += 1
            await db.flush()
            await db.refresh(existing)
            return existing

        item = WishlistItem(
            course_name=course_name,
            teacher_name=teacher_name,
            created_by=user_id,
            vote_count=1,
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    async def delete(self, db: AsyncSession, wish_id: int) -> bool:
        item = await db.get(WishlistItem, wish_id)
        if item is None:
            return False
        await db.delete(item)
        return True


wishlist_repo = WishlistRepository()
