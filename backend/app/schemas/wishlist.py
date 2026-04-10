from pydantic import BaseModel, ConfigDict, Field


class WishlistCreate(BaseModel):
    name: str
    teacher: str
    model_config = ConfigDict(populate_by_name=True)


class WishCourseOut(BaseModel):
    id: int
    name: str
    teacher: str
    vote_count: int = Field(alias="voteCount")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
