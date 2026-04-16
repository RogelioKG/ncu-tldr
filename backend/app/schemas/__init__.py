from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.schemas.course import (
    CourseOut,
    CoursePairOut,
    CoursePairsResponse,
    RatingsOut as CourseRatingsOut,
    SummaryOut,
    GradingItem,
)
from app.schemas.review import (
    ReviewCreate,
    CourseCommentOut,
    RatingsIn,
    RatingsOut as ReviewRatingsOut,
)
from app.schemas.comment import CommentCreate
from app.schemas.wishlist import WishCourseOut

__all__ = [
    "LoginRequest",
    "MessageResponse",
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
    "WishCourseOut",
]
