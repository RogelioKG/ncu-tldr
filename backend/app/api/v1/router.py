from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, comments, courses, reviews, wishlist

api_router = APIRouter(prefix="/v1")

api_router.include_router(courses.router)
api_router.include_router(comments.router)
api_router.include_router(reviews.router)
api_router.include_router(wishlist.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
