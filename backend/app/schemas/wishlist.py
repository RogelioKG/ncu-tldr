from pydantic import BaseModel, ConfigDict


class WishCourseOut(BaseModel):
    """Aggregated view of a course's wish votes."""

    course_id: int
    title: str
    vote_count: int
    has_voted: bool

    model_config = ConfigDict(from_attributes=True)
