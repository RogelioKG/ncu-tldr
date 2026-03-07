from app.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.schemas.common import CourseRatings
from app.schemas.course import Course, CourseSummary, GradingItem
from app.schemas.review import Review, ReviewCreate
from app.schemas.wish import WishCourse, WishCreate

__all__ = [
    "AuthTokenResponse",
    "Course",
    "CourseRatings",
    "CourseSummary",
    "GradingItem",
    "LoginRequest",
    "RegisterRequest",
    "Review",
    "ReviewCreate",
    "UserResponse",
    "WishCourse",
    "WishCreate",
]
