from pydantic import BaseModel


class CourseTimeOut(BaseModel):
    day: int
    period: str


class CourseOut(BaseModel):
    id: int
    externalId: int
    classNo: str
    title: str
    credit: int
    passwordCard: str
    limitCnt: int | None
    admitCnt: int
    waitCnt: int
    courseType: str
    lastSemester: str | None
    teachers: list[str]
    departments: list[str]
    colleges: list[str]
    times: list[CourseTimeOut]


class CoursePair(BaseModel):
    courseName: str
    teacher: str


class CoursePairsResponse(BaseModel):
    pairs: list[CoursePair]
