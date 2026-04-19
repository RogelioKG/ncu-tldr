import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Header,
    Body,
    Depends,
    HTTPException,
)
from sqlalchemy import text

from app.db.deps import get_db
from app.services.sync_courses import generate_course_sync_sql
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)


def verify_sync_secret_key(x_sync_secret_key: str = Header(...)):
    if x_sync_secret_key != get_settings().x_sync_secret_key:
        logger.warning("Legacy admin sync auth failed")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Key")
    logger.debug("Legacy admin sync auth succeeded")


async def sync_courses_task(raw_json: dict):
    logger.info("Legacy sync courses task started")
    sql_scripts = generate_course_sync_sql(raw_json)

    async for db in get_db():
        async with db.begin():
            for sql in sql_scripts:
                await db.execute(text(sql))
        break
    logger.info("Legacy sync courses task completed")


@router.post("/sync", status_code=202, dependencies=[Depends(verify_sync_secret_key)])
async def sync_courses(background_tasks: BackgroundTasks, payload: dict = Body(...)):
    logger.info("Legacy sync endpoint queued background job")
    background_tasks.add_task(sync_courses_task, payload)
    # CI 無法知道 background task 是否整合成功，僅能由後端日誌確定 (暫且從簡)
    return {"status": "accepted", "message": "Job queued"}
