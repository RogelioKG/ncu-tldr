from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_optional_user
from app.models.user import User
from app.schemas.wishlist import WishCourseOut, WishlistCreate
from app.services.wishlist_service import wishlist_service

router = APIRouter(tags=["wishlist"])


@router.get("", response_model=list[WishCourseOut])
async def list_wishlist(db: AsyncSession = Depends(get_db)):
    return await wishlist_service.list_wishes(db)


@router.post("", response_model=WishCourseOut, status_code=201)
async def add_to_wishlist(
    data: WishlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return await wishlist_service.add_wish(db, data, current_user)


@router.delete("/{wish_id}", status_code=204)
async def delete_from_wishlist(
    wish_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    await wishlist_service.delete_wish(db, wish_id, current_user)
    return Response(status_code=204)
