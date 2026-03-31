from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user
from app.models.course import Course
from app.models.teacher import Teacher
from app.models.user import User
from app.models.wish import Wish
from app.models.wish_vote import WishVote
from app.schemas.wish import WishCourse, WishCreate

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


def _to_wish_schema(wish: Wish) -> WishCourse:
    return WishCourse(
        id=wish.id,
        name=wish.course_name,
        teacher=wish.teacher,
        voteCount=wish.vote_count,
    )


@router.get(
    "",
    response_model=list[WishCourse],
)
async def get_wishlist(
    db: AsyncSession = Depends(get_db),
) -> list[WishCourse]:
    result = await db.execute(select(Wish).order_by(Wish.vote_count.desc()))
    return [_to_wish_schema(w) for w in result.scalars().all()]


@router.post(
    "",
    response_model=WishCourse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wish(
    payload: WishCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WishCourse:
    pair_exists = await db.execute(
        select(Course.id)
        .join(Teacher, Course.teacher_id == Teacher.id)
        .where(Course.name == payload.name, Teacher.name == payload.teacher)
        .limit(1)
    )
    if pair_exists.scalar_one_or_none() is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Invalid course-teacher pair",
        )

    result = await db.execute(select(Wish).where(Wish.course_name == payload.name, Wish.teacher == payload.teacher))
    existing = result.scalar_one_or_none()

    if existing is not None:
        already_voted = await db.execute(select(WishVote).where(WishVote.wish_id == existing.id, WishVote.user_id == user.id))
        if already_voted.scalar_one_or_none() is None:
            db.add(WishVote(wish_id=existing.id, user_id=user.id))
            await db.flush()
            count = (await db.execute(select(func.count()).select_from(WishVote).where(WishVote.wish_id == existing.id))).scalar_one()
            existing.vote_count = count
            await db.commit()
            await db.refresh(existing)
        return _to_wish_schema(existing)

    wish = Wish(
        course_name=payload.name,
        teacher=payload.teacher,
        created_by=user.id,
    )
    db.add(wish)
    await db.flush()

    db.add(WishVote(wish_id=wish.id, user_id=user.id))
    wish.vote_count = 1
    await db.commit()
    await db.refresh(wish)
    return _to_wish_schema(wish)


@router.post("/{wish_id}/vote", response_model=WishCourse)
async def toggle_vote(
    wish_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WishCourse:
    wish = await db.get(Wish, wish_id)
    if wish is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wish not found")

    existing_vote = await db.execute(select(WishVote).where(WishVote.wish_id == wish_id, WishVote.user_id == user.id))
    vote = existing_vote.scalar_one_or_none()

    if vote is not None:
        await db.execute(delete(WishVote).where(WishVote.wish_id == wish_id, WishVote.user_id == user.id))
    else:
        db.add(WishVote(wish_id=wish_id, user_id=user.id))

    await db.flush()

    count_result = await db.execute(select(func.count()).select_from(WishVote).where(WishVote.wish_id == wish_id))
    wish.vote_count = count_result.scalar_one()
    await db.commit()
    await db.refresh(wish)
    return _to_wish_schema(wish)


@router.delete("/{wish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wish(
    wish_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    wish = await db.get(Wish, wish_id)
    if wish is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wish not found")
    if wish.created_by != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the creator can delete")
    await db.delete(wish)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
