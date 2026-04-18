from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str
    parent_id: int | None = Field(alias="parentId", default=None)
    model_config = ConfigDict(populate_by_name=True)
