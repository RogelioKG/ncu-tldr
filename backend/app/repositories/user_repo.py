import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_utils import mask_email
from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> User | None:
        user = await db.get(User, user_id)
        if user is None:
            logger.warning("User not found by id user_id=%s", user_id)
        else:
            logger.debug("User loaded by id user_id=%s", user_id)
        return user

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        logger.debug("Lookup user by email email=%s", mask_email(email))
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        hashed_password: str,
        display_name: str,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            display_name=display_name,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        logger.info("User created user_id=%s email=%s", user.id, mask_email(user.email))
        return user


user_repo = UserRepository()
