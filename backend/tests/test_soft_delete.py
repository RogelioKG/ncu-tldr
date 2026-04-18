from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course


async def _register_and_verify(client: AsyncClient, student_id: str) -> str:
    captured: dict[str, str] = {}

    def capture(_email: str, token: str):
        captured["token"] = token
        return True

    with patch(
        "app.services.auth_service.send_verification_email", side_effect=capture
    ):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{student_id}@cc.ncu.edu.tw",
                "password": "pass123",
                "displayName": f"User{student_id[-3:]}",
            },
        )

    verify_resp = await client.get(
        "/api/v1/auth/verify-email",
        params={"token": captured["token"]},
    )
    return verify_resp.json()["accessToken"]


async def _create_course(
    db: AsyncSession, *, title: str, external_id: int, class_no: str
) -> int:
    course = Course(
        external_id=external_id,
        class_no=class_no,
        title=title,
        credit=3,
        course_type="REQUIRED",
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course.id


@pytest.mark.asyncio
async def test_soft_delete_review_hides_from_list(
    client: AsyncClient, db: AsyncSession
) -> None:
    token = await _register_and_verify(client, "100000201")
    headers = {"Authorization": f"Bearer {token}"}
    course_id = await _create_course(
        db,
        title="Soft Delete Review Course",
        external_id=900001,
        class_no="SDR-001",
    )

    create_resp = await client.post(
        f"/api/v1/courses/{course_id}/reviews",
        json={
            "semester": "114-1",
            "title": "Test Review",
            "content": "content",
            "ratings": {"gain": 4, "highScore": 4, "easiness": 3, "teacherStyle": 5},
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    review_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/courses/{course_id}/reviews/{review_id}",
        headers=headers,
    )
    assert delete_resp.status_code == 204

    list_resp = await client.get(f"/api/v1/courses/{course_id}/reviews")
    assert list_resp.status_code == 200
    assert list_resp.json() == []

    my_resp = await client.get("/api/v1/auth/me/reviews", headers=headers)
    assert my_resp.status_code == 200
    assert my_resp.json() == []


@pytest.mark.asyncio
async def test_soft_delete_comment_keeps_placeholder(
    client: AsyncClient, db: AsyncSession
) -> None:
    token = await _register_and_verify(client, "100000202")
    headers = {"Authorization": f"Bearer {token}"}
    course_id = await _create_course(
        db,
        title="Soft Delete Comment Course",
        external_id=900002,
        class_no="SDC-001",
    )

    create_resp = await client.post(
        f"/api/v1/courses/{course_id}/comments",
        json={"content": "to be deleted"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    comment_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/courses/{course_id}/comments/{comment_id}",
        headers=headers,
    )
    assert delete_resp.status_code == 204

    list_resp = await client.get(
        f"/api/v1/courses/{course_id}/comments", headers=headers
    )
    assert list_resp.status_code == 200
    rows = list_resp.json()
    assert len(rows) == 1
    assert rows[0]["id"] == comment_id
    assert rows[0]["isDeleted"] is True
    assert rows[0]["content"] == "此留言已刪除"
    assert rows[0]["canDelete"] is False
