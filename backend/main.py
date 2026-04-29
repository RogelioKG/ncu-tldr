import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.app_logging import setup_logging
from app.db.session import async_session
from app.repositories.refresh_token_repo import refresh_token_repo

settings = get_settings()
setup_logging(settings)
logger = logging.getLogger(__name__)

_CLEANUP_INTERVAL_SECONDS = 3600


async def _cleanup_expired_tokens() -> None:
    while True:
        try:
            async with async_session() as db, db.begin():
                await refresh_token_repo.delete_expired(db)
        except Exception:
            logger.exception("Failed to clean up expired refresh tokens")
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_cleanup_expired_tokens())
    logger.info(
        "Refresh token cleanup task started interval=%ds", _CLEANUP_INTERVAL_SECONDS
    )
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        logger.info("Refresh token cleanup task stopped")


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
logger.info(
    "FastAPI app initialized: name=%s version=%s",
    settings.app_name,
    settings.app_version,
)


@app.get("/health")
async def health() -> dict[str, str]:
    logger.debug("Health check endpoint called")
    return {"status": "ok"}
