from pydantic import BaseModel, Field

from app.schemas.common import CourseRatings


class ReviewCreate(BaseModel):
    user: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=2000)
    ratings: CourseRatings


class Review(BaseModel):
    id: int
    user: str
    title: str
    content: str
    date: str
    likes: int = 0
    dislikes: int = 0
