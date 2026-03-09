from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import CourseRatings
from app.schemas.review import Review


class GradingItem(BaseModel):
    label: str
    percentage: int


class CourseSummary(BaseModel):
    overview: str
    targetAudience: str
    textbook: str
    prerequisites: str
    weeklyHours: str
    gradingItems: list[GradingItem]
    notes: str
    reviewCount: int


class Course(BaseModel):
    id: int
    name: str
    teacher: str
    tags: list[str]
    ratings: CourseRatings
    department: str | None = None
    code: str | None = None
    time: str | None = None
    credits: int | None = None
    type: str | None = None
    summary: CourseSummary | None = None
    comments: list[Review] = Field(default_factory=list)


class CoursePair(BaseModel):
    courseName: str
    teacher: str


class CoursePairsResponse(BaseModel):
    pairs: list[CoursePair]
