from collections.abc import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session

logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        logger.debug("Database session opened")
        try:
            yield session
            await session.commit()
            logger.debug("Database session committed")
        except Exception:
            logger.exception("Database transaction failed; rolling back")
            await session.rollback()
            raise
        finally:
            logger.debug("Database session closed")
