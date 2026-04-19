"""
Example 04 — Test Auth Flow đầy đủ

Trong thực tế, copy file này vào tests/test_auth.py của Blog API project.
Các fixture giả định đã có từ conftest.py (ví dụ 03).
"""

# ============================================================
# Helpers
# ============================================================
"""
# ---- tests/helpers.py ----
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.security import hash_password


async def create_test_user(
    db: AsyncSession,
    *,
    email: str = "user@test.com",
    name: str = "Test User",
    password: str = "password123",
    role: str = "user",
) -> User:
    user = User(
        email=email,
        name=name,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_and_get_token(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/auth/login",
        data={"username": email, "password": password},   # form-data
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]
"""


# ============================================================
# Fixture tạo user + authenticated client
# ============================================================
"""
# ---- tests/conftest.py (append) ----
import pytest
from tests.helpers import create_test_user, login_and_get_token


@pytest.fixture
async def test_user(db):
    return await create_test_user(db)


@pytest.fixture
async def admin_user(db):
    return await create_test_user(db, email="admin@test.com", role="admin")


@pytest.fixture
async def auth_client(client, test_user):
    token = await login_and_get_token(client, "user@test.com", "password123")
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def admin_client(client, admin_user):
    token = await login_and_get_token(client, "admin@test.com", "password123")
    client.headers["Authorization"] = f"Bearer {token}"
    return client
"""


# ============================================================
# Auth tests
# ============================================================
"""
# ---- tests/test_auth.py ----
from httpx import AsyncClient


class TestRegister:
    async def test_register_creates_user(self, client: AsyncClient):
        response = await client.post("/auth/register", json={
            "email": "new@test.com", "name": "New", "password": "password123"
        })
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "new@test.com"
        assert "hashed_password" not in body   # không leak

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post("/auth/register", json={
            "email": test_user.email, "name": "X", "password": "password123"
        })
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post("/auth/register", json={
            "email": "new@test.com", "name": "N", "password": "short"
        })
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post("/auth/login", data={
            "username": "user@test.com", "password": "password123"
        })
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post("/auth/login", data={
            "username": "user@test.com", "password": "wrong"
        })
        assert response.status_code == 401

    async def test_login_nonexistent_email(self, client: AsyncClient):
        response = await client.post("/auth/login", data={
            "username": "nobody@test.com", "password": "password123"
        })
        # Quan trọng: cùng status + message với "wrong password"
        assert response.status_code == 401

    async def test_brute_force_blocked(self, client: AsyncClient, test_user):
        # Sai password 6 lần
        for _ in range(6):
            await client.post("/auth/login", data={
                "username": "user@test.com", "password": "wrong"
            })
        # Lần thứ 7 (có thể lần thứ 6 đã bị block tùy policy)
        response = await client.post("/auth/login", data={
            "username": "user@test.com", "password": "password123"   # ngay cả đúng
        })
        assert response.status_code == 429


class TestProtectedRoutes:
    async def test_me_without_token(self, client: AsyncClient):
        response = await client.get("/users/me")
        assert response.status_code == 401

    async def test_me_with_invalid_token(self, client: AsyncClient):
        client.headers["Authorization"] = "Bearer invalid.token.here"
        response = await client.get("/users/me")
        assert response.status_code == 401

    async def test_me_with_valid_token(self, auth_client: AsyncClient, test_user):
        response = await auth_client.get("/users/me")
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email


class TestOwnership:
    async def test_user_cannot_edit_others_post(
        self, auth_client: AsyncClient, db
    ):
        # Seed post của user khác
        from app.models import Post, User
        from app.security import hash_password
        other = User(email="other@x.com", name="Other", hashed_password=hash_password("x"))
        db.add(other); await db.commit(); await db.refresh(other)
        post = Post(title="T", slug="t", content="C", author_id=other.id)
        db.add(post); await db.commit(); await db.refresh(post)

        response = await auth_client.patch(f"/posts/{post.id}", json={"title": "Hack"})
        assert response.status_code == 403

    async def test_admin_can_edit_any_post(
        self, admin_client: AsyncClient, db
    ):
        from app.models import Post, User
        from app.security import hash_password
        other = User(email="o@x.com", name="O", hashed_password=hash_password("x"))
        db.add(other); await db.commit(); await db.refresh(other)
        post = Post(title="T", slug="t", content="C", author_id=other.id)
        db.add(post); await db.commit(); await db.refresh(post)

        response = await admin_client.patch(f"/posts/{post.id}", json={"title": "Admin edit"})
        assert response.status_code == 200


class TestRefresh:
    async def test_refresh_rotates_token(self, client: AsyncClient, test_user):
        # Login
        r = await client.post("/auth/login", data={
            "username": "user@test.com", "password": "password123"
        })
        tokens = r.json()

        # Refresh
        r2 = await client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert r2.status_code == 200
        new_tokens = r2.json()
        assert new_tokens["access_token"] != tokens["access_token"]
        assert new_tokens["refresh_token"] != tokens["refresh_token"]

    async def test_refresh_with_access_token_fails(self, client: AsyncClient, test_user):
        r = await client.post("/auth/login", data={
            "username": "user@test.com", "password": "password123"
        })
        access = r.json()["access_token"]

        # Dùng access token thay refresh → fail
        r2 = await client.post("/auth/refresh", json={"refresh_token": access})
        assert r2.status_code == 401
"""


# ============================================================
# Test parametrize scenario
# ============================================================
"""
import pytest

@pytest.mark.parametrize(
    "email,password,expected_status",
    [
        ("valid@x.com", "password123", 200),
        ("valid@x.com", "wrong", 401),
        ("nobody@x.com", "anything", 401),
        ("", "password123", 422),          # empty email
        ("valid@x.com", "", 422),           # empty password
    ],
)
async def test_login_scenarios(
    client, test_user, email, password, expected_status,
):
    response = await client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == expected_status
"""


# ============================================================
# Bài tập
# ============================================================
#
# 1. Hoàn thiện test suite trên cho Blog API của bạn:
#    - Copy vào tests/test_auth.py
#    - Sửa import cho khớp project
#    - Chạy pytest, fix gì fail
#
# 2. Thêm test:
#    - Change password: đổi password rồi login bằng password cũ → 401
#    - Logout: logout rồi dùng refresh → 401
#    - Admin ban user: user bị ban → không login được
#
# 3. Đo coverage cho module auth:
#    uv run pytest --cov=app.auth --cov-report=term-missing tests/test_auth.py
#    → đảm bảo > 90%
