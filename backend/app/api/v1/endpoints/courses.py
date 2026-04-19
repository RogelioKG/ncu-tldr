import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.schemas.course import CourseOut, CoursePairsResponse
from app.services.course_service import course_service

router = APIRouter(tags=["courses"])
logger = logging.getLogger(__name__)


# IMPORTANT: /pairs must be BEFORE /{course_id} to avoid routing conflict
@router.get("/pairs", response_model=CoursePairsResponse)
async def get_pairs(db: AsyncSession = Depends(get_db)):
    logger.debug("Get pairs endpoint called")
    return await course_service.get_pairs(db)


@router.get("", response_model=list[CourseOut])
async def list_courses(
    q: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    slots: Annotated[list[str], Query()] = [],
    db: AsyncSession = Depends(get_db),
):
    logger.debug(
        "List courses endpoint q=%s sort=%s slots_count=%s", q, sort, len(slots)
    )
    return await course_service.list_courses(db, q=q, sort=sort, slots=slots)


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    logger.debug("Get course endpoint course_id=%s", course_id)
    course = await course_service.get_course(db, course_id)
    if course is None:
        logger.warning("Get course endpoint not found course_id=%s", course_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    return course
