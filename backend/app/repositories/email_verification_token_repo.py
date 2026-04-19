import uuid
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification_token import EmailVerificationToken

logger = logging.getLogger(__name__)


class EmailVerificationTokenRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        token: str,
    ) -> EmailVerificationToken:
        record = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        logger.debug("Email verification token created user_id=%s", user_id)
        return record

    async def get_by_token(
        self, db: AsyncSession, token: str
    ) -> EmailVerificationToken | None:
        logger.debug("Lookup email verification token")
        result = await db.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token == token)
        )
        return result.scalar_one_or_none()

    async def mark_used(self, db: AsyncSession, record: EmailVerificationToken) -> None:
        record.used_at = datetime.now(timezone.utc)
        await db.flush()
        logger.debug("Email verification token marked used user_id=%s", record.user_id)


email_verification_token_repo = EmailVerificationTokenRepository()
