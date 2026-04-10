from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.schemas.course import CourseOut, CoursePairsResponse
from app.services.course_service import course_service

router = APIRouter(tags=["courses"])


# IMPORTANT: /pairs must be BEFORE /{course_id} to avoid routing conflict
@router.get("/pairs", response_model=CoursePairsResponse)
async def get_pairs(db: AsyncSession = Depends(get_db)):
    return await course_service.get_pairs(db)


@router.get("", response_model=list[CourseOut])
async def list_courses(
    q: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await course_service.list_courses(db, q=q, sort=sort)


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await course_service.get_course(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    return course
