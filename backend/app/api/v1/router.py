from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, comments, courses, reviews, wishlist

api_router = APIRouter(prefix="/v1")

api_router.include_router(admin.router,    prefix="/admin",   tags=["admin"])
api_router.include_router(auth.router,     prefix="/auth",    tags=["auth"])
api_router.include_router(courses.router,  prefix="/courses", tags=["courses"])
api_router.include_router(reviews.router,  prefix="/courses", tags=["reviews"])
api_router.include_router(comments.router, prefix="/courses", tags=["comments"])
api_router.include_router(wishlist.router, prefix="/wishlist", tags=["wishlist"])
