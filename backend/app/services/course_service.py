from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.repositories.course_repo import course_repo
from app.schemas.course import (
    CoursePairOut,
    CoursePairsResponse,
    CourseOut,
    RatingsOut,
    SummaryOut,
)

_DAY_MAP = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日"}

SORT_FIELD_MAP = {
    "reward": "gain",
    "score": "high_score",
    "easiness": "easiness",
    "teacherStyle": "teacher_style",
}


def _parse_sort(sort: str | None) -> tuple[str | None, str]:
    if not sort:
        return None, "desc"
    parts = sort.split(":", 1)
    field = SORT_FIELD_MAP.get(parts[0])
    direction = parts[1] if len(parts) > 1 and parts[1] in ("asc", "desc") else "desc"
    return field, direction


def _format_teacher_names(course: Course) -> str:
    if not course.course_teachers:
        return ""
    sorted_teachers = sorted(
        course.course_teachers,
        key=lambda ct: ct.sort_order if ct.sort_order is not None else 0,
    )
    return "、".join(ct.teacher.name for ct in sorted_teachers if ct.teacher)


def _format_time(times: list) -> str | None:
    if not times:
        return None
    parts = []
    for t in times:
        day_str = _DAY_MAP.get(t.day, str(t.day))
        parts.append(f"{day_str}{t.period}")
    return " / ".join(parts) if parts else None


def _get_department(course: Course) -> str | None:
    if not course.course_departments:
        return None
    first = course.course_departments[0]
    if first.department:
        return first.department.name
    return None


def _to_course_out(
    row: tuple,
    include_summary: bool = False,
) -> CourseOut:
    course, avg_gain, avg_high_score, avg_easiness, avg_teacher_style, review_count = (
        row
    )

    summary = None
    if include_summary:
        summary = SummaryOut(
            overview="",
            target_audience="",
            textbook="",
            prerequisites="",
            weekly_hours="",
            grading_items=[],
            notes="",
            review_count=int(review_count or 0),
        )

    return CourseOut(
        id=course.id,
        name=course.title,
        teacher=_format_teacher_names(course),
        tags=[],
        ratings=RatingsOut(
            gain=float(avg_gain),
            high_score=float(avg_high_score),
            easiness=float(avg_easiness),
            teacher_style=float(avg_teacher_style),
        ),
        semester=course.last_semester,
        department=_get_department(course),
        code=course.class_no,
        time=_format_time(course.course_times),
        credits=course.credit,
        type=course.course_type,
        summary=summary,
    )


class CourseService:
    async def list_courses(
        self,
        db: AsyncSession,
        q: str | None = None,
        sort: str | None = None,
    ) -> list[CourseOut]:
        sort_field, sort_dir = _parse_sort(sort)
        rows = await course_repo.list_courses(
            db, q=q, sort_field=sort_field, sort_dir=sort_dir
        )
        return [_to_course_out(row) for row in rows]

    async def get_course(self, db: AsyncSession, course_id: int) -> CourseOut:
        course = await course_repo.get_by_id(db, course_id)
        if course is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
        avg_ratings = await course_repo.get_avg_ratings(db, course_id)
        review_count = await course_repo.get_review_count(db, course_id)
        row = (
            course,
            avg_ratings["gain"],
            avg_ratings["high_score"],
            avg_ratings["easiness"],
            avg_ratings["teacher_style"],
            review_count,
        )
        return _to_course_out(row, include_summary=True)

    async def get_pairs(self, db: AsyncSession) -> CoursePairsResponse:
        pairs = await course_repo.get_pairs(db)
        return CoursePairsResponse(
            pairs=[
                CoursePairOut(
                    course_name=row.title, teacher=row.name, course_id=row.course_id
                )
                for row in pairs
            ]
        )


course_service = CourseService()
