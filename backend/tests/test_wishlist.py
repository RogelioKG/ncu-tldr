from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course


def _student_email() -> str:
    student_id = str(uuid4().int % 1_000_000_000).zfill(9)
    return f"{student_id}@cc.ncu.edu.tw"


async def _register_and_verify(client: AsyncClient) -> None:
    captured: dict[str, str] = {}

    def capture(email: str, token: str) -> bool:
        captured["token"] = token
        return True

    email = _student_email()
    with patch(
        "app.services.auth_service.send_verification_email", side_effect=capture
    ):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "pass123",
                "displayName": f"User-{email[:9]}",
            },
        )
    assert resp.status_code == 200

    verify_resp = await client.get(
        "/api/v1/auth/verify-email", params={"token": captured["token"]}
    )
    assert verify_resp.status_code == 200
    # Cookies are now set on the client automatically — no token returned


async def _create_course(db: AsyncSession, *, title: str) -> int:
    external_id = int(uuid4().int % 1_000_000_000)
    course = Course(
        external_id=external_id,
        class_no=f"CLS-{external_id}",
        title=title,
        credit=3,
        password_card="NONE",
        limit_cnt=60,
        admit_cnt=0,
        wait_cnt=0,
        course_type="ELECTIVE",
        last_semester="1131",
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course.id


@pytest.mark.asyncio
async def test_list_wishlist_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/wishlist")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_vote_for_course_requires_auth(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    course_id = await _create_course(db, title="Machine Learning")
    resp = await client.post(f"/api/v1/wishlist/{course_id}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_vote_for_course_success_and_visible_in_list(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    course_id = await _create_course(db, title="Distributed Systems")
    await _register_and_verify(client)

    # httpx AsyncClient auto-sends cookies set during _register_and_verify
    vote_resp = await client.post(f"/api/v1/wishlist/{course_id}")
    assert vote_resp.status_code == 204

    list_resp = await client.get("/api/v1/wishlist")
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert len(payload) == 1

    item = payload[0]
    assert item["course_id"] == course_id
    assert item["title"] == "Distributed Systems"
    assert item["vote_count"] == 1
    assert item["has_voted"] is True


@pytest.mark.asyncio
async def test_vote_for_same_course_twice_returns_conflict(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    course_id = await _create_course(db, title="Operating Systems")
    await _register_and_verify(client)

    # httpx AsyncClient auto-sends cookies set during _register_and_verify
    first = await client.post(f"/api/v1/wishlist/{course_id}")
    second = await client.post(f"/api/v1/wishlist/{course_id}")

    assert first.status_code == 204
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_vote_for_missing_course_returns_not_found(client: AsyncClient) -> None:
    await _register_and_verify(client)
    resp = await client.post("/api/v1/wishlist/2147483647")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_wishlist_not_found(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    course_id = await _create_course(db, title="Not Voted Yet")
    await _register_and_verify(client)
    resp = await client.delete(f"/api/v1/wishlist/{course_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_wishlist_success(client: AsyncClient, db: AsyncSession) -> None:
    course_id = await _create_course(db, title="Course To Unvote")
    await _register_and_verify(client)

    # httpx AsyncClient auto-sends cookies set during _register_and_verify
    create_resp = await client.post(f"/api/v1/wishlist/{course_id}")
    assert create_resp.status_code == 204

    del_resp = await client.delete(f"/api/v1/wishlist/{course_id}")
    assert del_resp.status_code == 204

    list_resp = await client.get("/api/v1/wishlist")
    course_ids = [item["course_id"] for item in list_resp.json()]
    assert course_id not in course_ids
