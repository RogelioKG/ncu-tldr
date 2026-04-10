from pydantic import BaseModel, ConfigDict, Field


class RatingsIn(BaseModel):
    gain: int  # 1-5
    high_score: int = Field(alias="highScore")  # 1-5
    easiness: int  # 1-5
    teacher_style: int = Field(alias="teacherStyle")  # 1-5
    model_config = ConfigDict(populate_by_name=True)


class ReviewCreate(BaseModel):
    title: str = ""
    content: str
    ratings: RatingsIn
    model_config = ConfigDict(populate_by_name=True)


class RatingsOut(BaseModel):
    gain: float
    high_score: float = Field(alias="highScore")
    easiness: float
    teacher_style: float = Field(alias="teacherStyle")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CourseCommentOut(BaseModel):
    id: int
    user: str  # display_name of the user
    title: str
    content: str
    date: str  # ISO format date string
    likes: int
    dislikes: int
    parent_id: int | None = Field(alias="parentId", default=None)
    ratings: RatingsOut | None = None  # Only present for reviews, not comments
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
