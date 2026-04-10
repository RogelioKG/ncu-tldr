from sqlalchemy import Float, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.course_department import CourseDepartment
from app.models.course_teacher import CourseTeacher
from app.models.course_time import CourseTime
from app.models.department import Department
from app.models.review import Review
from app.models.teacher import Teacher


class CourseRepository:
    def _ratings_subquery(self):
        return (
            select(
                Review.course_id,
                func.avg(Review.gain).label("avg_gain"),
                func.avg(Review.high_score).label("avg_high_score"),
                func.avg(Review.easiness).label("avg_easiness"),
                func.avg(Review.teacher_style).label("avg_teacher_style"),
                func.count(Review.id).label("review_count"),
            )
            .group_by(Review.course_id)
            .subquery()
        )

    async def list_courses(
        self,
        db: AsyncSession,
        q: str | None = None,
        sort_field: str | None = None,
        sort_dir: str = "desc",
    ) -> list[tuple]:
        if sort_dir not in ("asc", "desc"):
            sort_dir = "desc"
        ratings_sq = self._ratings_subquery()

        stmt = (
            select(
                Course,
                func.coalesce(cast(ratings_sq.c.avg_gain, Float), 0.0).label("avg_gain"),
                func.coalesce(cast(ratings_sq.c.avg_high_score, Float), 0.0).label("avg_high_score"),
                func.coalesce(cast(ratings_sq.c.avg_easiness, Float), 0.0).label("avg_easiness"),
                func.coalesce(cast(ratings_sq.c.avg_teacher_style, Float), 0.0).label("avg_teacher_style"),
                func.coalesce(ratings_sq.c.review_count, 0).label("review_count"),
            )
            .outerjoin(ratings_sq, ratings_sq.c.course_id == Course.id)
            .options(
                selectinload(Course.course_teachers).selectinload(CourseTeacher.teacher),
                selectinload(Course.course_times),
                selectinload(Course.course_departments).selectinload(CourseDepartment.department),
            )
        )

        if q:
            stmt = (
                stmt
                .outerjoin(CourseTeacher, CourseTeacher.course_id == Course.id)
                .outerjoin(Teacher, Teacher.id == CourseTeacher.teacher_id)
                .where(
                    or_(
                        Course.title.ilike(f"%{q}%"),
                        Teacher.name.ilike(f"%{q}%"),
                    )
                )
                .distinct()
            )

        sort_col_map = {
            "gain": ratings_sq.c.avg_gain,
            "high_score": ratings_sq.c.avg_high_score,
            "easiness": ratings_sq.c.avg_easiness,
            "teacher_style": ratings_sq.c.avg_teacher_style,
        }

        if sort_field and sort_field in sort_col_map:
            col = sort_col_map[sort_field]
            order_expr = col.desc() if sort_dir == "desc" else col.asc()
        else:
            order_expr = Course.id.asc()

        stmt = stmt.order_by(order_expr)

        result = await db.execute(stmt)
        return list(result.all())

    async def get_by_id(self, db: AsyncSession, course_id: int) -> Course | None:
        result = await db.execute(
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.course_teachers).selectinload(CourseTeacher.teacher),
                selectinload(Course.course_times),
                selectinload(Course.course_departments).selectinload(CourseDepartment.department),
            )
        )
        return result.scalars().first()

    async def get_pairs(self, db: AsyncSession) -> list:
        result = await db.execute(
            select(Course.title, Teacher.name)
            .join(CourseTeacher, CourseTeacher.course_id == Course.id)
            .join(Teacher, Teacher.id == CourseTeacher.teacher_id)
            .order_by(Course.title, Teacher.name)
        )
        return result.all()

    async def get_review_count(self, db: AsyncSession, course_id: int) -> int:
        result = await db.execute(
            select(func.count(Review.id)).where(Review.course_id == course_id)
        )
        return result.scalar_one()

    async def get_avg_ratings(self, db: AsyncSession, course_id: int) -> dict:
        result = await db.execute(
            select(
                func.avg(Review.gain).label("avg_gain"),
                func.avg(Review.high_score).label("avg_high_score"),
                func.avg(Review.easiness).label("avg_easiness"),
                func.avg(Review.teacher_style).label("avg_teacher_style"),
            ).where(Review.course_id == course_id)
        )
        row = result.first()
        if row is None or row.avg_gain is None:
            return {
                "gain": 0.0,
                "high_score": 0.0,
                "easiness": 0.0,
                "teacher_style": 0.0,
            }
        return {
            "gain": float(row.avg_gain),
            "high_score": float(row.avg_high_score),
            "easiness": float(row.avg_easiness),
            "teacher_style": float(row.avg_teacher_style),
        }


course_repo = CourseRepository()
