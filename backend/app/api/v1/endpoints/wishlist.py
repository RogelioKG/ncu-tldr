from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.wishlist import WishCourseOut
from app.services.wishlist_service import wishlist_service

router = APIRouter(tags=["wishlist"])


@router.get("", response_model=list[WishCourseOut])
async def list_wishlist(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    user_id = current_user.id if current_user is not None else None
    return await wishlist_service.list_wishes(db, user_id=user_id)


@router.post("/{course_id}", status_code=204)
async def vote_for_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await wishlist_service.add_vote(db, course_id=course_id, user_id=current_user.id)
    return Response(status_code=204)


@router.delete("/{course_id}", status_code=204)
async def unvote_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await wishlist_service.remove_vote(db, course_id=course_id, user_id=current_user.id)
    return Response(status_code=204)
