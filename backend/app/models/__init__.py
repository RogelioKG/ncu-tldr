from app.models.college import College
from app.models.course import Course
from app.models.course_college import CourseCollege
from app.models.course_department import CourseDepartment
from app.models.course_teacher import CourseTeacher
from app.models.course_time import CourseTime
from app.models.department import Department
from app.models.metadata import Metadata
from app.models.teacher import Teacher

__all__ = [
    "College",
    "Course",
    "CourseCollege",
    "CourseDepartment",
    "CourseTeacher",
    "CourseTime",
    "Department",
    "Metadata",
    "Teacher",
]
