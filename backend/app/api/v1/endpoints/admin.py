import logging

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Header, HTTPException
from sqlalchemy import text

from app.config import get_settings
from app.db.deps import get_db
from app.services.sync_courses import generate_course_sync_sql

router = APIRouter(tags=["admin"])
logger = logging.getLogger(__name__)


def verify_sync_secret_key(x_sync_secret_key: str = Header(...)):
    if x_sync_secret_key != get_settings().x_sync_secret_key:
        logger.warning("Admin sync auth failed: invalid x-sync-secret-key")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Key")
    logger.debug("Admin sync auth succeeded")


async def sync_courses_task(raw_json: dict):
    logger.info("Sync courses background task started")
    sql_scripts = generate_course_sync_sql(raw_json)
    logger.debug("Sync courses generated sql_count=%s", len(sql_scripts))

    async for db in get_db():
        async with db.begin():
            for sql in sql_scripts:
                await db.execute(text(sql))
        break
    logger.info("Sync courses background task completed")


@router.post("/sync", status_code=202, dependencies=[Depends(verify_sync_secret_key)])
async def sync_courses(background_tasks: BackgroundTasks, payload: dict = Body(...)):
    logger.info("Sync courses endpoint queued background job")
    background_tasks.add_task(sync_courses_task, payload)
    return {"status": "accepted", "message": "Job queued"}
