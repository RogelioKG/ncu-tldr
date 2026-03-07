from pydantic import BaseModel


class CourseRatings(BaseModel):
    reward: float
    score: float
    easiness: float
    teacherStyle: float
