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


def verify_sync_secret_key(x_sync_secret_key: str = Header(...)):
    if x_sync_secret_key != get_settings().x_sync_secret_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Key")


async def sync_courses_task(raw_json: dict):
    sql_scripts = generate_course_sync_sql(raw_json)

    async for db in get_db():
        async with db.begin():
            for sql in sql_scripts:
                await db.execute(text(sql))
        break


@router.post("/sync", status_code=202, dependencies=[Depends(verify_sync_secret_key)])
async def sync_courses(background_tasks: BackgroundTasks, payload: dict = Body(...)):
    background_tasks.add_task(sync_courses_task, payload)
    # CI 無法知道 background task 是否整合成功，僅能由後端日誌確定 (暫且從簡)
    return {"status": "accepted", "message": "Job queued"}
