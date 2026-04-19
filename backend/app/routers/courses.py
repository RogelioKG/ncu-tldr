from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.deps import get_db
from app.models.course import Course as CourseModel
from app.models.course_teacher import CourseTeacher
from app.models.teacher import Teacher
from app.schemas.course import CourseOut, CoursePair, CoursePairsResponse, CourseTimeOut

router = APIRouter(prefix="/courses", tags=["courses"])
logger = logging.getLogger(__name__)

_SORT_FIELD_MAP: dict[str, str] = {
    "title": "title",
    "credit": "credit",
    "updatedAt": "updated_at",
}


def _to_course_schema(row: CourseModel) -> CourseOut:
    teachers = sorted(row.course_teachers, key=lambda ct: ct.sort_order or 0)
    return CourseOut(
        id=row.id,
        externalId=row.external_id,
        classNo=row.class_no,
        title=row.title,
        credit=row.credit,
        passwordCard=row.password_card,
        limitCnt=row.limit_cnt,
        admitCnt=row.admit_cnt,
        waitCnt=row.wait_cnt,
        courseType=row.course_type,
        lastSemester=row.last_semester,
        teachers=[ct.teacher.name for ct in teachers],
        departments=[cd.department.name for cd in row.course_departments],
        colleges=[cc.college.name for cc in row.course_colleges],
        times=[CourseTimeOut(day=ct.day, period=ct.period) for ct in row.course_times],
    )


@router.get("", response_model=list[CourseOut])
async def get_courses(
    q: str | None = Query(default=None, description="Search keyword"),
    sort: str | None = Query(
        default=None,
        description="Sort: title, credit, updatedAt (append :asc for ascending)",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[CourseOut]:
    logger.debug("Legacy get_courses called q=%s sort=%s", q, sort)
    from app.models.course_college import CourseCollege
    from app.models.course_department import CourseDepartment

    stmt = select(CourseModel).options(
        selectinload(CourseModel.course_teachers).joinedload(CourseTeacher.teacher),
        selectinload(CourseModel.course_departments).joinedload(
            CourseDepartment.department
        ),
        selectinload(CourseModel.course_colleges).joinedload(CourseCollege.college),
        selectinload(CourseModel.course_times),
    )

    if q:
        keyword = f"%{q.strip()}%"
        stmt = stmt.where(
            CourseModel.title.ilike(keyword)
            | CourseModel.course_teachers.any(
                CourseTeacher.teacher.has(Teacher.name.ilike(keyword))
            )
        )

    sort_field_name, descending = _parse_sort(sort)
    db_col_name = _SORT_FIELD_MAP.get(sort_field_name, "title")
    col = getattr(CourseModel, db_col_name)
    stmt = stmt.order_by(col.desc() if descending else col.asc())

    result = await db.execute(stmt)
    rows = result.unique().scalars().all()
    return [_to_course_schema(r) for r in rows]


@router.get("/pairs", response_model=CoursePairsResponse)
async def get_course_pairs(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> CoursePairsResponse:
    logger.debug("Legacy get_course_pairs called")
    stmt = (
        select(CourseModel.title, Teacher.name.label("teacher_name"))
        .join(CourseTeacher, CourseModel.id == CourseTeacher.course_id)
        .join(Teacher, CourseTeacher.teacher_id == Teacher.id)
        .distinct()
        .order_by(CourseModel.title, Teacher.name)
    )
    result = await db.execute(stmt)
    pairs = [
        CoursePair(courseName=row.title, teacher=row.teacher_name)
        for row in result.all()
    ]
    response.headers["Cache-Control"] = "public, max-age=3600"
    return CoursePairsResponse(pairs=pairs)


@router.get("/{course_id}", response_model=CourseOut)
async def get_course_by_id(
    course_id: int,
    db: AsyncSession = Depends(get_db),
) -> CourseOut:
    logger.debug("Legacy get_course_by_id called course_id=%s", course_id)
    from app.models.course_college import CourseCollege
    from app.models.course_department import CourseDepartment

    stmt = (
        select(CourseModel)
        .options(
            selectinload(CourseModel.course_teachers).joinedload(CourseTeacher.teacher),
            selectinload(CourseModel.course_departments).joinedload(
                CourseDepartment.department
            ),
            selectinload(CourseModel.course_colleges).joinedload(CourseCollege.college),
            selectinload(CourseModel.course_times),
        )
        .where(CourseModel.id == course_id)
    )
    result = await db.execute(stmt)
    row = result.unique().scalar_one_or_none()
    if row is None:
        logger.warning("Legacy get_course_by_id not found course_id=%s", course_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Course {course_id} not found")
    return _to_course_schema(row)


def _parse_sort(sort: str | None) -> tuple[str, bool]:
    if not sort:
        return "title", False
    normalized = sort.strip()
    if ":" in normalized:
        field, direction = normalized.split(":", 1)
        return field, direction.lower() != "asc"
    if normalized.startswith("-"):
        return normalized[1:], True
    return normalized, False
