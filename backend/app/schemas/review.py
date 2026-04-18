from pydantic import BaseModel, ConfigDict, Field


class RatingsIn(BaseModel):
    gain: int | None = None
    high_score: int | None = Field(alias="highScore", default=None)
    easiness: int | None = None
    teacher_style: int | None = Field(alias="teacherStyle", default=None)
    model_config = ConfigDict(populate_by_name=True)


class ReviewCreate(BaseModel):
    semester: str
    title: str = ""
    content: str | None = None
    ratings: RatingsIn | None = None
    weekly_hours: int | None = Field(alias="weeklyHours", default=None)
    textbook: str | None = None
    model_config = ConfigDict(populate_by_name=True)


class RatingsOut(BaseModel):
    gain: float | None = None
    high_score: float | None = Field(alias="highScore", default=None)
    easiness: float | None = None
    teacher_style: float | None = Field(alias="teacherStyle", default=None)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CourseCommentOut(BaseModel):
    id: int
    user: str
    title: str
    content: str | None
    date: str
    likes: int
    dislikes: int
    parent_id: int | None = Field(alias="parentId", default=None)
    is_deleted: bool = Field(alias="isDeleted", default=False)
    can_delete: bool = Field(alias="canDelete", default=False)
    ratings: RatingsOut | None = None
    semester: str | None = None
    weekly_hours: int | None = Field(alias="weeklyHours", default=None)
    textbook: str | None = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MyReviewOut(CourseCommentOut):
    course_name: str = Field(alias="courseName")
    course_id: int = Field(alias="courseId")
