from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.deps import get_db
from app.models.course import Course as CourseModel
from app.models.teacher import Teacher
from app.schemas.common import CourseRatings
from app.schemas.course import Course, CoursePair, CoursePairsResponse

router = APIRouter(prefix="/courses", tags=["courses"])

_SORT_FIELD_MAP: dict[str, str] = {
    "reward": "avg_reward",
    "score": "avg_score",
    "easiness": "avg_easiness",
    "teacherStyle": "avg_teacher_style",
    "overall": "avg_overall",
}


def _to_course_schema(row: CourseModel) -> Course:
    return Course(
        id=row.id,
        name=row.name,
        teacher=row.teacher.name if row.teacher else "",
        tags=[],
        ratings=CourseRatings(
            reward=float(row.avg_reward),
            score=float(row.avg_score),
            easiness=float(row.avg_easiness),
            teacherStyle=float(row.avg_teacher_style),
        ),
        department=row.department.name if row.department else None,
        code=row.course_code,
        time=row.schedule,
        credits=row.credits,
        type=row.course_type,
    )


@router.get("", response_model=list[Course])
async def get_courses(
    q: str | None = Query(default=None, description="Search keyword"),
    sort: str | None = Query(
        default=None,
        description="Sort: overall, reward, score, easiness, teacherStyle (append :asc for ascending)",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[Course]:
    stmt = select(CourseModel).options(
        joinedload(CourseModel.teacher), joinedload(CourseModel.department)
    )

    if q:
        keyword = f"%{q.strip()}%"
        stmt = stmt.where(
            CourseModel.name.ilike(keyword) | Teacher.name.ilike(keyword)
        ).join(Teacher, CourseModel.teacher_id == Teacher.id)
    else:
        stmt = stmt.join(Teacher, CourseModel.teacher_id == Teacher.id)

    sort_field_name, reverse = _parse_sort(sort)
    db_col_name = _SORT_FIELD_MAP.get(sort_field_name, "avg_overall")
    col = getattr(CourseModel, db_col_name)
    stmt = stmt.order_by(col.desc() if reverse else col.asc())

    result = await db.execute(stmt)
    rows = result.unique().scalars().all()
    return [_to_course_schema(r) for r in rows]


@router.get("/pairs", response_model=CoursePairsResponse)
async def get_course_pairs(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> CoursePairsResponse:
    stmt = (
        select(CourseModel.name, Teacher.name.label("teacher_name"))
        .join(Teacher, CourseModel.teacher_id == Teacher.id)
        .distinct()
        .order_by(CourseModel.name, Teacher.name)
    )
    result = await db.execute(stmt)
    pairs = [
        CoursePair(courseName=row.name, teacher=row.teacher_name)
        for row in result.all()
    ]
    response.headers["Cache-Control"] = "public, max-age=3600"
    return CoursePairsResponse(pairs=pairs)


@router.get("/{course_id}", response_model=Course)
async def get_course_by_id(
    course_id: int,
    db: AsyncSession = Depends(get_db),
) -> Course:
    stmt = (
        select(CourseModel)
        .options(joinedload(CourseModel.teacher), joinedload(CourseModel.department))
        .where(CourseModel.id == course_id)
    )
    result = await db.execute(stmt)
    row = result.unique().scalar_one_or_none()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Course {course_id} not found")
    return _to_course_schema(row)


def _parse_sort(sort: str | None) -> tuple[str, bool]:
    if not sort:
        return "overall", True
    normalized = sort.strip()
    if ":" in normalized:
        field, direction = normalized.split(":", 1)
        return field, direction.lower() != "asc"
    if normalized.startswith("-"):
        return normalized[1:], True
    return normalized, False
