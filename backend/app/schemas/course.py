from pydantic import BaseModel, ConfigDict, Field


class RatingsOut(BaseModel):
    gain: float = 0.0
    high_score: float = Field(alias="highScore", default=0.0)
    easiness: float = 0.0
    teacher_style: float = Field(alias="teacherStyle", default=0.0)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class GradingItem(BaseModel):
    label: str
    percentage: int


class SummaryOut(BaseModel):
    overview: str = ""
    target_audience: str = Field(alias="targetAudience", default="")
    textbook: str = ""
    prerequisites: str = ""
    weekly_hours: str = Field(alias="weeklyHours", default="")
    grading_items: list[GradingItem] = Field(alias="gradingItems", default_factory=list)
    notes: str = ""
    review_count: int = Field(alias="reviewCount", default=0)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CourseOut(BaseModel):
    id: int
    name: str
    teacher: str  # Joined teacher names e.g. "张三、李四"
    tags: list[str] = []
    ratings: RatingsOut
    semester: str | None = None
    department: str | None = None
    code: str | None = None
    time: str | None = None
    credits: int | None = None
    type: str | None = None
    summary: SummaryOut | None = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CoursePairOut(BaseModel):
    course_id: int = Field(alias="courseId")
    course_name: str = Field(alias="courseName")
    teacher: str
    model_config = ConfigDict(populate_by_name=True)


class CoursePairsResponse(BaseModel):
    pairs: list[CoursePairOut]
    model_config = ConfigDict(populate_by_name=True)
