from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from threading import Lock
from uuid import uuid4

from fastapi import HTTPException, status

from app.schemas.auth import UserResponse
from app.schemas.review import Review, ReviewCreate
from app.schemas.wish import WishCourse, WishCreate


class MockDB:
    def __init__(self) -> None:
        self._lock = Lock()
        self._seed()

    def _seed(self) -> None:
        self._courses: list[dict] = [
            {
                "id": 1,
                "name": "演算法",
                "teacher": "王大明",
                "tags": ["找對組員重要", "高分", "作業多", "實用"],
                "ratings": {
                    "reward": 4.5,
                    "score": 4.0,
                    "easiness": 3.0,
                    "teacherStyle": 4.5,
                },
                "schoolDept": "資訊工程學系",
                "code": "CS3001",
                "time": "四234",
                "credits": 3,
                "type": "必修",
                "summary": {
                    "overview": "本課程介紹演算法設計與分析。",
                    "targetAudience": "具備程式與資料結構基礎者。",
                    "textbook": "老師講義",
                    "prerequisites": "資料結構",
                    "weeklyHours": "6-8小時",
                    "gradingItems": [
                        {"label": "作業", "percentage": 40},
                        {"label": "期中", "percentage": 30},
                        {"label": "期末", "percentage": 30},
                    ],
                    "notes": "期中考較難，作業實作為主。",
                    "reviewCount": 2,
                },
                "comments": [
                    {
                        "id": 1,
                        "user": "User1",
                        "title": "老師教得很好",
                        "content": "作業偏多但學到很多。",
                        "date": "2026/02/20",
                        "likes": 12,
                        "dislikes": 1,
                        "ratings": {
                            "reward": 5.0,
                            "score": 4.0,
                            "easiness": 3.0,
                            "teacherStyle": 5.0,
                        },
                    },
                    {
                        "id": 2,
                        "user": "User2",
                        "title": "考試難度高",
                        "content": "要提早複習，題目偏觀念。",
                        "date": "2026/02/22",
                        "likes": 8,
                        "dislikes": 0,
                        "ratings": {
                            "reward": 4.0,
                            "score": 4.0,
                            "easiness": 3.0,
                            "teacherStyle": 4.0,
                        },
                    },
                ],
            },
            {
                "id": 2,
                "name": "資料結構",
                "teacher": "陳教授",
                "tags": ["實用", "程式作業"],
                "ratings": {
                    "reward": 4.8,
                    "score": 4.2,
                    "easiness": 3.2,
                    "teacherStyle": 4.3,
                },
                "schoolDept": "資訊工程學系",
                "code": "CS2001",
                "time": "三234",
                "credits": 3,
                "type": "必修",
                "comments": [],
            },
            {
                "id": 3,
                "name": "線性代數",
                "teacher": "林博士",
                "tags": ["基礎重要", "考試多"],
                "ratings": {
                    "reward": 4.0,
                    "score": 3.5,
                    "easiness": 2.0,
                    "teacherStyle": 3.5,
                },
                "schoolDept": "數學系",
                "code": "MA1001",
                "time": "一234",
                "credits": 3,
                "type": "必修",
                "comments": [],
            },
        ]
        self._wishes: list[dict] = [
            {"id": 1, "name": "演算法", "teacher": "王大明", "voteCount": 4},
            {"id": 2, "name": "動力學", "teacher": "廖老大", "voteCount": 2},
            {
                "id": 3,
                "name": "當代潮流與兩性探討",
                "teacher": "蘇勃起",
                "voteCount": 1,
            },
        ]
        self._users: dict[str, dict] = {
            "demo@ncu.edu.tw": {
                "id": 1,
                "email": "demo@ncu.edu.tw",
                "displayName": "Demo User",
                "password": "password123",
                "isActive": True,
            }
        }
        self._token_to_email: dict[str, str] = {}

    def reset(self) -> None:
        with self._lock:
            self._seed()

    def list_courses(self, q: str | None, sort: str | None) -> list[dict]:
        with self._lock:
            courses = deepcopy(self._courses)

        if q:
            keyword = q.strip().lower()
            courses = [
                c
                for c in courses
                if keyword in c["name"].lower()
                or keyword in c["teacher"].lower()
                or any(keyword in tag.lower() for tag in c["tags"])
            ]

        sort_field, reverse = self._parse_sort(sort)
        courses.sort(
            key=lambda course: self._course_sort_value(course, sort_field),
            reverse=reverse,
        )
        return courses

    def get_course(self, course_id: int) -> dict:
        with self._lock:
            for course in self._courses:
                if course["id"] == course_id:
                    return deepcopy(course)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found",
        )

    def get_reviews(self, course_id: int) -> list[Review]:
        course = self.get_course(course_id)
        return [
            Review.model_validate(self._strip_review_rating(r))
            for r in course["comments"]
        ]

    def add_review(self, course_id: int, payload: ReviewCreate) -> Review:
        with self._lock:
            for course in self._courses:
                if course["id"] != course_id:
                    continue
                next_id = max((r["id"] for r in course["comments"]), default=0) + 1
                review = {
                    "id": next_id,
                    "user": payload.user,
                    "title": payload.title,
                    "content": payload.content,
                    "date": datetime.now().strftime("%Y/%m/%d"),
                    "likes": 0,
                    "dislikes": 0,
                    "ratings": payload.ratings.model_dump(),
                }
                course["comments"].append(review)
                self._recalculate_course_rating(course)
                return Review.model_validate(self._strip_review_rating(review))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found",
        )

    def list_wishlist(self) -> list[WishCourse]:
        with self._lock:
            data = deepcopy(self._wishes)
        data.sort(key=lambda row: row["voteCount"], reverse=True)
        return [WishCourse.model_validate(wish) for wish in data]

    def add_wish(self, payload: WishCreate) -> WishCourse:
        with self._lock:
            for wish in self._wishes:
                if wish["name"] == payload.name and wish["teacher"] == payload.teacher:
                    wish["voteCount"] += 1
                    return WishCourse.model_validate(deepcopy(wish))
            next_id = max((w["id"] for w in self._wishes), default=0) + 1
            new_wish = {
                "id": next_id,
                "name": payload.name,
                "teacher": payload.teacher,
                "voteCount": 1,
            }
            self._wishes.append(new_wish)
            return WishCourse.model_validate(deepcopy(new_wish))

    def remove_wish(self, wish_id: int) -> None:
        with self._lock:
            for idx, wish in enumerate(self._wishes):
                if wish["id"] == wish_id:
                    self._wishes.pop(idx)
                    return
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wish {wish_id} not found",
        )

    def register(
        self, email: str, password: str, display_name: str
    ) -> tuple[str, UserResponse]:
        with self._lock:
            if email in self._users:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            next_id = max((user["id"] for user in self._users.values()), default=0) + 1
            self._users[email] = {
                "id": next_id,
                "email": email,
                "displayName": display_name,
                "password": password,
                "isActive": True,
            }
            token = f"mock-{uuid4().hex}"
            self._token_to_email[token] = email
            return token, self._to_user_response(self._users[email])

    def login(self, email: str, password: str) -> tuple[str, UserResponse]:
        with self._lock:
            user = self._users.get(email)
            if user is None or user["password"] != password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )
            token = f"mock-{uuid4().hex}"
            self._token_to_email[token] = email
            return token, self._to_user_response(user)

    def get_user_by_token(self, token: str) -> UserResponse:
        with self._lock:
            email = self._token_to_email.get(token)
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            user = self._users[email]
            return self._to_user_response(user)

    @staticmethod
    def _strip_review_rating(review: dict) -> dict:
        copied = deepcopy(review)
        copied.pop("ratings", None)
        return copied

    @staticmethod
    def _to_user_response(user: dict) -> UserResponse:
        return UserResponse(
            id=user["id"],
            email=user["email"],
            displayName=user["displayName"],
            isActive=user["isActive"],
        )

    @staticmethod
    def _parse_sort(sort: str | None) -> tuple[str, bool]:
        if not sort:
            return "overall", True
        normalized = sort.strip()
        if ":" in normalized:
            field, direction = normalized.split(":", 1)
            reverse = direction.lower() != "asc"
            return field, reverse
        if normalized.startswith("-"):
            return normalized[1:], True
        return normalized, False

    @staticmethod
    def _course_sort_value(course: dict, sort_field: str) -> float:
        ratings = course["ratings"]
        if sort_field == "overall":
            return (
                ratings["reward"]
                + ratings["score"]
                + ratings["easiness"]
                + ratings["teacherStyle"]
            ) / 4
        if sort_field in ratings:
            return ratings[sort_field]
        return 0.0

    @staticmethod
    def _recalculate_course_rating(course: dict) -> None:
        comments = course["comments"]
        if not comments:
            return
        reward = sum(c["ratings"]["reward"] for c in comments) / len(comments)
        score = sum(c["ratings"]["score"] for c in comments) / len(comments)
        easiness = sum(c["ratings"]["easiness"] for c in comments) / len(comments)
        teacher_style = sum(c["ratings"]["teacherStyle"] for c in comments) / len(
            comments
        )
        course["ratings"] = {
            "reward": round(reward, 2),
            "score": round(score, 2),
            "easiness": round(easiness, 2),
            "teacherStyle": round(teacher_style, 2),
        }
        if "summary" in course and course["summary"] is not None:
            course["summary"]["reviewCount"] = len(comments)


mock_db = MockDB()
