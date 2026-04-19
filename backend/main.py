import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.app_logging import setup_logging

settings = get_settings()
setup_logging(settings)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version)
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
