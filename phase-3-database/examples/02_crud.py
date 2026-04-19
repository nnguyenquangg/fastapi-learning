"""
Example 02 — Model + CRUD Cơ Bản

SQLAlchemy 2.0 declarative với `Mapped[...]`.
Layer: routers → services → repositories → models.

Cấu trúc đề xuất cho project thực:
    app/
      db.py              # engine, SessionLocal, get_db
      models/
        __init__.py
        base.py          # Base class
        user.py
        product.py
      repositories/
        user_repo.py
        product_repo.py
      services/
        user_service.py
      routers/
        users.py
      schemas/
        user.py

Ở file này gộp lại cho dễ đọc.
"""
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# --- Import từ example 01 (trong project thật sẽ import từ app.db) ---
from .connection import DbDep  # noqa — giả lập


# ============================================================
# 1. Base model
# ============================================================
class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# 2. Model User
# ============================================================
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r})"


# ============================================================
# 3. Pydantic schemas
# ============================================================
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    is_active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # đọc từ ORM object

    id: int
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime


class UsersPage(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    size: int


# ============================================================
# 4. Repository (SQL query sạch, không business logic)
# ============================================================
class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return await self.db.scalar(stmt)

    async def list(self, *, page: int, size: int) -> tuple[list[User], int]:
        offset = (page - 1) * size
        items_stmt = select(User).order_by(User.id).offset(offset).limit(size)
        items = list((await self.db.scalars(items_stmt)).all())

        # Count riêng (KHÔNG dùng len(items) trên page nhỏ - sai total)
        from sqlalchemy import func
        count_stmt = select(func.count(User.id))
        total = await self.db.scalar(count_stmt) or 0

        return items, total

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()      # để có id, chưa commit
        await self.db.refresh(user)
        return user

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()


# ============================================================
# 5. Service (business logic, quyết định commit)
# ============================================================
def hash_password(raw: str) -> str:
    """Phase 4 sẽ dùng bcrypt thật."""
    return f"hashed::{raw}"


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email đã được sử dụng",
            )
        user = User(
            email=data.email,
            name=data.name,
            hashed_password=hash_password(data.password),
        )
        user = await self.repo.create(user)
        await self.db.commit()    # ← quyết định commit ở service
        return user

    async def get(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get(user_id)
        user = await self.repo.update(user, data.model_dump(exclude_unset=True))
        await self.db.commit()
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get(user_id)
        await self.repo.delete(user)
        await self.db.commit()

    async def list(self, page: int, size: int) -> UsersPage:
        items, total = await self.repo.list(page=page, size=size)
        return UsersPage(
            items=[UserRead.model_validate(u) for u in items],
            total=total, page=page, size=size,
        )


def get_user_service(db: DbDep) -> UserService:
    return UserService(db)


ServiceDep = Annotated[UserService, Depends(get_user_service)]


# ============================================================
# 6. Router
# ============================================================
app = FastAPI()


@app.post("/users", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, svc: ServiceDep) -> User:
    return await svc.register(payload)


@app.get("/users", response_model=UsersPage)
async def list_users(svc: ServiceDep, page: int = 1, size: int = 20) -> UsersPage:
    return await svc.list(page, size)


@app.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, svc: ServiceDep) -> User:
    return await svc.get(user_id)


@app.patch("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, svc: ServiceDep) -> User:
    return await svc.update(user_id, payload)


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, svc: ServiceDep) -> None:
    await svc.delete(user_id)


# === Điểm quan trọng cần ghi nhớ ===
#
# 1. SQLAlchemy 2.0 style:
#    - Dùng Mapped[int], mapped_column(...) — không dùng Column(...) cũ
#    - Dùng select(...), await session.scalar(stmt) / scalars(stmt).all()
#    - Không dùng session.query(...) (legacy style)
#
# 2. `from_attributes=True` thay cho `orm_mode` (V1):
#    Cho phép Pydantic đọc từ ORM object
#
# 3. Tách layer:
#    - Repository: chỉ truy vấn DB, không raise HTTPException
#    - Service: business logic, raise HTTPException, commit
#    - Router: parse request, trả response
#
# 4. `session.flush()` vs `session.commit()`:
#    - flush: gửi SQL xuống DB nhưng chưa commit → dùng trong transaction
#    - commit: chốt transaction
#    - Service: flush nhiều, commit một lần cuối
#
# 5. count dùng func.count() riêng, KHÔNG dùng len(items) vì items chỉ là 1 page
