from pydantic import BaseModel, ConfigDict, Field


class CommentOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    user: str = "匿名"
    title: str | None = None
    content: str
    date: str
    likes: int = 0
    dislikes: int = 0
    parent_id: int | None = Field(default=None, alias="parentId", serialization_alias="parentId")


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    title: str | None = Field(default=None, max_length=200)
    parent_id: int | None = Field(default=None, alias="parentId", serialization_alias="parentId")

    model_config = ConfigDict(populate_by_name=True)
