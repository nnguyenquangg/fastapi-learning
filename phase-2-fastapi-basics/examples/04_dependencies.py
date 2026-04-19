"""
Example 04 — APIRouter & Dependency Injection

Cấu trúc project chuẩn + `Depends`.

Chạy: uv run fastapi dev examples/04_dependencies.py
"""
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel


# ============================================================
# Part 1: APIRouter
# ============================================================

# Giả sử trong project thực:
#   app/
#     main.py
#     routers/
#       users.py
#       posts.py

users_router = APIRouter(prefix="/users", tags=["users"])
posts_router = APIRouter(prefix="/posts", tags=["posts"])


@users_router.get("/")
async def list_users() -> list[dict]:
    return [{"id": 1, "name": "An"}]


@users_router.get("/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "An"}


@posts_router.get("/")
async def list_posts() -> list[dict]:
    return [{"id": 1, "title": "Hello"}]


# ============================================================
# Part 2: Dependency cơ bản
# ============================================================

# Dependency = function/callable có trả về gì đó, FastAPI gọi giúp
# Dùng cho:
# - Common query params (pagination)
# - DB session
# - Auth (lấy current user từ token)
# - Cache connection
# - ...

class Pagination(BaseModel):
    page: int
    size: int
    offset: int


async def pagination_params(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Pagination:
    return Pagination(page=page, size=size, offset=(page - 1) * size)


# Type alias cho gọn (pattern rất phổ biến):
PaginationDep = Annotated[Pagination, Depends(pagination_params)]


@users_router.get("/paginated/all")
async def list_users_paginated(pg: PaginationDep) -> dict:
    return {"page": pg.page, "size": pg.size, "offset": pg.offset}


# ============================================================
# Part 3: Dependency trả về service/resource
# ============================================================

class UserService:
    def __init__(self) -> None:
        self._users: dict[int, dict] = {1: {"id": 1, "name": "An"}}

    async def get(self, user_id: int) -> dict | None:
        return self._users.get(user_id)

    async def create(self, name: str) -> dict:
        new_id = max(self._users.keys(), default=0) + 1
        user = {"id": new_id, "name": name}
        self._users[new_id] = user
        return user


def get_user_service() -> UserService:
    """Trong thực tế: trả về service có inject DB session."""
    return UserService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@users_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(name: str, svc: UserServiceDep) -> dict:
    return await svc.create(name)


# ============================================================
# Part 4: Auth dependency (preview - Phase 4 sâu hơn)
# ============================================================

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """Parse header Authorization: Bearer <token>."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.removeprefix("Bearer ")
    # Fake: token = user_id
    if token == "invalid":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": int(token), "name": f"User {token}"}


CurrentUserDep = Annotated[dict, Depends(get_current_user)]


@users_router.get("/me")
async def me(user: CurrentUserDep) -> dict:
    return user


# ============================================================
# Part 5: Dependency tầng (sub-dependency)
# ============================================================

async def require_admin(user: CurrentUserDep) -> dict:
    """Depend vào get_current_user + check role."""
    # Giả lập: user id 1 là admin
    if user["id"] != 1:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


AdminDep = Annotated[dict, Depends(require_admin)]


@users_router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, _: AdminDep) -> None:
    # Chỉ admin mới gọi được
    return None


# ============================================================
# Part 6: Dependency với yield (teardown)
# ============================================================

async def get_db():
    """Pattern chuẩn cho DB session. Phase 3 sẽ dùng thật."""
    db = {"connection": "open"}   # giả lập
    print("DB opened")
    try:
        yield db
    finally:
        print("DB closed")
        db["connection"] = "closed"


DbDep = Annotated[dict, Depends(get_db)]


@posts_router.get("/with-db")
async def with_db(db: DbDep) -> dict:
    return db


# ============================================================
# Lắp ráp app
# ============================================================

app = FastAPI(title="Dependency Demo")
app.include_router(users_router)
app.include_router(posts_router)


# === Bài tập ===
#
# 1. Viết dependency `sorting_params(sort_by, order)`:
#    - sort_by: Literal["name", "created_at", "id"]
#    - order: Literal["asc", "desc"]
#    - Trả về tuple (str, str)
#
# 2. Viết router `/products` với include: GET list (có pagination + sorting),
#    POST tạo, GET {id}, DELETE {id} (cần admin)
#
# 3. Viết dependency `get_current_user_optional` trả về User | None
#    (nếu có token thì parse, không có → None)
#    Dùng cho endpoint public nhưng có optional personalization
