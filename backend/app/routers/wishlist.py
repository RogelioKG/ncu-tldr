from fastapi import APIRouter, Response, status

from app.schemas.wish import WishCourse, WishCreate
from app.services.mock_db import mock_db

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=list[WishCourse])
async def get_wishlist() -> list[WishCourse]:
    return mock_db.list_wishlist()


@router.post("", response_model=WishCourse, status_code=201)
async def create_wish(payload: WishCreate) -> WishCourse:
    return mock_db.add_wish(payload=payload)


@router.delete("/{wish_id}", status_code=204)
async def delete_wish(wish_id: int) -> Response:
    mock_db.remove_wish(wish_id=wish_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
