from fastapi import APIRouter, Query

from app.schemas.course import Course
from app.services.mock_db import mock_db

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[Course])
async def get_courses(
    q: str | None = Query(default=None, description="Search keyword"),
    sort: str | None = Query(
        default=None, description="Sort: overall, reward, score, easiness, teacherStyle"
    ),
) -> list[Course]:
    rows = mock_db.list_courses(q=q, sort=sort)
    return [Course.model_validate(row) for row in rows]


@router.get("/{course_id}", response_model=Course)
async def get_course_by_id(course_id: int) -> Course:
    row = mock_db.get_course(course_id=course_id)
    return Course.model_validate(row)
