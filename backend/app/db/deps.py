from collections.abc import AsyncGenerator
import logging

from fastapi import HTTPException
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
        except HTTPException as exc:
            await session.rollback()
            if 400 <= exc.status_code < 500:
                logger.info(
                    "HTTPException during DB dependency status=%s; rolled back transaction",
                    exc.status_code,
                )
            else:
                logger.warning(
                    "HTTPException during DB dependency status=%s; rolled back transaction",
                    exc.status_code,
                )
            raise
        except Exception:
            logger.exception("Database transaction failed; rolling back")
            await session.rollback()
            raise
        finally:
            logger.debug("Database session closed")
