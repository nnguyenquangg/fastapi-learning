"""
Example 01 — Connect FastAPI với PostgreSQL async

Mô hình:
    Settings (pydantic-settings)
        ↓
    Engine (async)
        ↓
    SessionMaker
        ↓
    get_db dependency → endpoint

Chạy:
    uv run fastapi dev examples/01_connection.py
"""
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


# ============================================================
# 1. Settings
# ============================================================
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/phase3"
    echo_sql: bool = False   # True khi debug, log mọi query


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ============================================================
# 2. Engine & Session
# ============================================================
def make_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        echo=settings.echo_sql,
        pool_size=10,         # số connection giữ sẵn
        max_overflow=20,      # burst thêm
        pool_pre_ping=True,   # check connection trước khi dùng (tránh stale)
    )


settings = get_settings()
engine = make_engine(settings)
SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,   # object vẫn dùng được sau commit
    autoflush=False,
)


# ============================================================
# 3. get_db dependency
# ============================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Mỗi request một session.
    Rollback nếu exception, close sau cùng.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # commit ở service layer, không auto commit ở đây


DbDep = Annotated[AsyncSession, Depends(get_db)]


# ============================================================
# 4. FastAPI app + health check
# ============================================================
app = FastAPI(title="DB Connection Demo")


@app.get("/health/db")
async def health_db(db: DbDep) -> dict:
    """Ping DB để confirm connection."""
    result = await db.execute(text("SELECT 1 AS ok"))
    row = result.first()
    return {"db": "up", "ok": row.ok if row else None}


@app.get("/db/version")
async def db_version(db: DbDep) -> dict:
    result = await db.execute(text("SELECT version()"))
    return {"version": result.scalar()}


@app.get("/db/products")
async def db_products(db: DbDep, limit: int = 5) -> list[dict]:
    # Dùng SQL thuần (raw) - chỉ cho ví dụ
    # Trong thực tế → dùng ORM (ví dụ 02)
    result = await db.execute(
        text("SELECT id, name, price FROM products ORDER BY id LIMIT :limit"),
        {"limit": limit},
    )
    return [dict(row._mapping) for row in result]


# ============================================================
# 5. Lifecycle (shutdown engine đúng cách)
# ============================================================
@app.on_event("shutdown")
async def shutdown() -> None:
    await engine.dispose()


# === Note quan trọng ===
#
# 1. URL format: postgresql+asyncpg://user:pass@host:port/dbname
#    - asyncpg = driver async (nhanh nhất)
#    - ❌ KHÔNG dùng psycopg2 (sync)
#
# 2. pool_size + max_overflow:
#    - Số connection tối đa app mở = pool_size + max_overflow
#    - Tính dựa vào workers và DB max_connections (default PG: 100)
#
# 3. expire_on_commit=False:
#    - Default True: sau commit, object "expire" → access attr → lazy reload
#    - Async + expire_on_commit=True → lỗi MissingGreenlet
#    - Luôn set False trong async
#
# 4. echo=True khi debug, TẮT trong production (log rất nhiều)
#
# 5. pool_pre_ping: bật để tránh "connection closed" sau khi idle
#
# 6. Tại sao KHÔNG commit trong get_db?
#    - Commit = quyết định của business logic (service)
#    - get_db chỉ đảm bảo rollback nếu exception và close
