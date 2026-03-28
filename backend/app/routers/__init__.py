from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.comments import router as comments_router
from app.routers.courses import router as courses_router
from app.routers.reviews import router as reviews_router
from app.routers.wishlist import router as wishlist_router

__all__ = [
    "admin_router",
    "auth_router",
    "comments_router",
    "courses_router",
    "reviews_router",
    "wishlist_router",
]
