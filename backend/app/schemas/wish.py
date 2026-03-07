from pydantic import BaseModel, Field


class WishCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    teacher: str = Field(min_length=1, max_length=100)


class WishCourse(BaseModel):
    id: int
    name: str
    teacher: str
    voteCount: int = 1
