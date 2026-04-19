"""
Example 03 — Test với PostgreSQL thật

Chiến lược:
- Test DB RIÊNG (không dùng production DB 🚨)
- conftest.py tạo engine + sessionmaker riêng
- Mỗi test: tạo session, làm việc, rollback (hoặc truncate) sau

Đây là pattern mình khuyến khích cho FastAPI project.
"""

# ============================================================
# conftest.py (ở root tests/)
# ============================================================
# ---- tests/conftest.py ----
"""
import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.db import Base, get_db
from app.main import app


# --- Settings override ---
def override_settings() -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/blog_api_test",
        jwt_secret="test-secret-32-bytes-aaaaaaaaaaaa",
        environment="test",
    )


app.dependency_overrides[get_settings] = override_settings
TEST_SETTINGS = override_settings()


# --- Test engine (1 lần cho cả session) ---
@pytest.fixture(scope="session")
def event_loop():
    # pytest-asyncio cần single loop cho session-scoped async fixture
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_SETTINGS.database_url, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


# --- Per-test session với rollback ---
@pytest.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    # Pattern: mỗi test trong transaction riêng, rollback ở cuối
    # → test không ảnh hưởng nhau, chạy nhanh
    async with engine.connect() as conn:
        trans = await conn.begin()
        Session = async_sessionmaker(bind=conn, expire_on_commit=False)
        session = Session()

        # Nested savepoint để code app có thể commit() mà không thoát transaction outer
        nested = await conn.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(session_, transaction):
            nonlocal nested
            if not nested.is_active:
                nested = conn.sync_connection.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


# --- AsyncClient dùng session test ---
@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override get_db để endpoint dùng session test
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
"""

# ============================================================
# Ví dụ test endpoint có DB
# ============================================================
# ---- tests/test_users.py ----
"""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def test_register_creates_user_in_db(client: AsyncClient, db: AsyncSession):
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "name": "Test",
        "password": "password123",
    })
    assert response.status_code == 201

    # Verify trong DB
    from sqlalchemy import select
    user = await db.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    assert user.name == "Test"
    # Password phải được hash
    assert user.hashed_password != "password123"


async def test_register_duplicate_email_returns_409(client: AsyncClient, db: AsyncSession):
    # Seed 1 user trước
    db.add(User(email="dup@x.com", name="First", hashed_password="x"))
    await db.commit()

    response = await client.post("/auth/register", json={
        "email": "dup@x.com",
        "name": "Second",
        "password": "password123",
    })
    assert response.status_code == 409


async def test_list_users_pagination(client: AsyncClient, db: AsyncSession):
    # Seed 25 user
    for i in range(25):
        db.add(User(email=f"u{i}@x.com", name=f"User {i}", hashed_password="x"))
    await db.commit()

    response = await client.get("/users?page=1&size=10")
    body = response.json()
    assert body["total"] == 25
    assert len(body["items"]) == 10

    response = await client.get("/users?page=3&size=10")
    body = response.json()
    assert len(body["items"]) == 5   # page cuối chỉ có 5 user
"""


# ============================================================
# Setup DB test
# ============================================================
# 1. Tạo DB riêng cho test:
#
#    docker exec -it learn-pg psql -U postgres -c "CREATE DATABASE blog_api_test;"
#
# 2. Environment:
#
#    Có thể tạo .env.test, hoặc set inline:
#    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/blog_api_test uv run pytest
#
# 3. Trong CI: service Postgres tạm thời, xem .github/workflows/ci.yml


# ============================================================
# Chiến lược isolation
# ============================================================
#
# A. Transaction rollback (khuyến khích - nhanh nhất)
#    - Mỗi test trong transaction, rollback cuối
#    - Cần savepoint nếu code app gọi commit()
#    - Con trỏ serial/sequence không reset → test nên dùng unique data
#
# B. Truncate tables (đơn giản)
#    - Chạy TRUNCATE trước/sau mỗi test
#    - Chậm hơn A nhưng dễ hiểu
#
# C. Recreate schema (không khuyến khích)
#    - drop_all + create_all mỗi test → rất chậm
#    - Chỉ dùng cho test migration
#
# D. Testcontainers
#    - Mỗi test run spin up Postgres container riêng
#    - Chậm nhưng isolation tuyệt đối
#    - Dùng: uv add --dev testcontainers


# ============================================================
# Tips tránh flaky test
# ============================================================
#
# 1. KHÔNG phụ thuộc thứ tự test:
#    - pytest mặc định chạy theo thứ tự file, nhưng đừng rely
#    - `pytest-randomly` để random thứ tự → lộ dependency ẩn
#
# 2. KHÔNG dùng fixed date/time:
#    - datetime.utcnow() trong code → test lúc nửa đêm fail
#    - Dùng freezegun hoặc DI clock service
#
# 3. KHÔNG dùng fixed id:
#    - Serial sequence không reset → test lần 2 fail vì id khác
#    - Test nên assert field khác (email), hoặc grep id từ response
#
# 4. Seed data minimal cho mỗi test:
#    - Tạo đủ context cho test đó, không hơn không kém
#    - Dùng factory (vd factory_boy) cho gọn


# ============================================================
# Bài tập
# ============================================================
#
# 1. Viết conftest.py thật cho Blog API của bạn:
#    - engine session-scoped
#    - db fixture per-test với rollback
#    - client fixture override get_db
#    Chạy thử 1 test CRUD đơn giản
#
# 2. Fixture `authenticated_client`:
#    - Tạo user
#    - Login, lấy token
#    - Return client đã set header Authorization
#    Dùng trong test endpoint cần auth
#
# 3. Factory dùng factory_boy:
#    class UserFactory(factory.Factory):
#        class Meta:
#            model = User
#        email = factory.Sequence(lambda n: f"user{n}@x.com")
#        name = factory.Faker("name")
#        hashed_password = "hashed::x"
#    → dùng trong test: user = UserFactory.create()
#
# 4. Bench test: chạy 50 test xem mất bao lâu
#    Nếu > 30s → check: rollback ok chưa, có test nào hit network không
"""
