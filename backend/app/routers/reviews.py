from fastapi import APIRouter

from app.schemas.review import Review, ReviewCreate
from app.services.mock_db import mock_db

router = APIRouter(prefix="/courses/{course_id}/reviews", tags=["reviews"])


@router.get("", response_model=list[Review])
async def get_reviews(course_id: int) -> list[Review]:
    return mock_db.get_reviews(course_id=course_id)


@router.post("", response_model=Review, status_code=201)
async def create_review(course_id: int, payload: ReviewCreate) -> Review:
    return mock_db.add_review(course_id=course_id, payload=payload)
