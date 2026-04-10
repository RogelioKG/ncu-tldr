from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str
    title: str | None = None
    parent_id: int | None = Field(alias="parentId", default=None)
    model_config = ConfigDict(populate_by_name=True)
