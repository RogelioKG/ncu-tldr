import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

logger = logging.getLogger(__name__)


class RefreshTokenRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        db.add(token)
        await db.flush()
        await db.refresh(token)
        logger.debug("Refresh token created user_id=%s", user_id)
        return token

    async def get_by_hash(
        self, db: AsyncSession, token_hash: str
    ) -> RefreshToken | None:
        logger.debug("Refresh token lookup by hash")
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalars().first()

    async def revoke(self, db: AsyncSession, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await db.flush()
        logger.info("Refresh token revoked user_id=%s", token.user_id)

    async def revoke_all_for_user(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.flush()
        logger.warning("All refresh tokens revoked user_id=%s", user_id)

    async def delete_expired(self, db: AsyncSession) -> int:
        result = await db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        await db.flush()
        count = result.rowcount
        if count:
            logger.info("Deleted %d expired refresh tokens", count)
        return count


refresh_token_repo = RefreshTokenRepository()
