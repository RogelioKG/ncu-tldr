from pydantic import BaseModel, ConfigDict, Field


class WishCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    teacher: str = Field(min_length=1, max_length=100)


class WishCourse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    teacher: str
    voteCount: int = Field(default=1, alias="voteCount")
