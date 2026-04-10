from app.schemas.auth import LoginRequest, RegisterRequest, UserOut, TokenResponse
from app.schemas.course import CourseOut, CoursePairOut, CoursePairsResponse, RatingsOut as CourseRatingsOut, SummaryOut, GradingItem
from app.schemas.review import ReviewCreate, CourseCommentOut, RatingsIn, RatingsOut as ReviewRatingsOut
from app.schemas.comment import CommentCreate
from app.schemas.wishlist import WishlistCreate, WishCourseOut

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "UserOut",
    "TokenResponse",
    "CourseOut",
    "CoursePairOut",
    "CoursePairsResponse",
    "CourseRatingsOut",
    "SummaryOut",
    "GradingItem",
    "ReviewCreate",
    "CourseCommentOut",
    "RatingsIn",
    "ReviewRatingsOut",
    "CommentCreate",
    "WishlistCreate",
    "WishCourseOut",
]
