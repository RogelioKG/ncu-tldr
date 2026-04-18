from app.models.college import College
from app.models.comment import Comment
from app.models.email_verification_token import EmailVerificationToken
from app.models.course import Course
from app.models.course_college import CourseCollege
from app.models.course_department import CourseDepartment
from app.models.course_teacher import CourseTeacher
from app.models.course_time import CourseTime
from app.models.department import Department
from app.models.metadata import Metadata
from app.models.refresh_token import RefreshToken
from app.models.review import Review
from app.models.teacher import Teacher
from app.models.user import User
from app.models.wishlist import WishlistVote

__all__ = [
    "College",
    "Comment",
    "EmailVerificationToken",
    "Course",
    "CourseCollege",
    "CourseDepartment",
    "CourseTeacher",
    "CourseTime",
    "Department",
    "Metadata",
    "RefreshToken",
    "Review",
    "Teacher",
    "User",
    "WishlistVote",
]
