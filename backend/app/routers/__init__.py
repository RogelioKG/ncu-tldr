from app.routers.auth import router as auth_router
from app.routers.courses import router as courses_router
from app.routers.reviews import router as reviews_router
from app.routers.wishlist import router as wishlist_router

__all__ = [
    "auth_router",
    "courses_router",
    "reviews_router",
    "wishlist_router",
]
