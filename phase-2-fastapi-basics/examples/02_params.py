"""
Example 02 — Path, Query, Body Parameters

Chạy: uv run fastapi dev examples/02_params.py
"""
from typing import Annotated

from fastapi import FastAPI, Path, Query, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()


# === 1. Path parameter ===
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    """FastAPI tự convert str → int và validate."""
    return {"user_id": user_id}


# Với constraint:
@app.get("/items/{item_id}")
async def get_item(
    item_id: Annotated[int, Path(ge=1, le=1000, description="ID item, 1-1000")],
) -> dict:
    return {"item_id": item_id}


# === 2. Query parameter ===
@app.get("/search")
async def search(
    q: Annotated[str, Query(min_length=2, max_length=50)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    return {"q": q, "limit": limit, "offset": offset}


# Optional query (có thể None):
@app.get("/items")
async def list_items(
    category: str | None = None,
    in_stock: bool = True,
) -> dict:
    return {"category": category, "in_stock": in_stock}


# === 3. Request body (Pydantic) ===
class UserCreate(BaseModel):
    """Schema cho input POST /users."""

    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=150)


class UserResponse(BaseModel):
    """Schema cho output - CHỈ field nào muốn trả về."""

    id: int
    email: EmailStr
    name: str


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(payload: UserCreate) -> dict:
    # Giả lập lưu DB, trả về user có id
    return {
        "id": 1,
        "email": payload.email,
        "name": payload.name,
        # age không xuất hiện trong UserResponse → bị filter ra
    }


# === 4. Path + Body ===
class UserUpdate(BaseModel):
    """PATCH: tất cả field optional."""

    name: str | None = Field(default=None, min_length=2)
    age: int | None = Field(default=None, ge=0, le=150)


@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserUpdate) -> dict:
    # Chỉ update field nào được gửi
    updated = payload.model_dump(exclude_unset=True)
    return {"id": user_id, "email": "stub@x.com", "name": updated.get("name", "old")}


# === Bài tập ===
#
# 1. Thêm endpoint GET /products?category=&min_price=&max_price=
#    - category optional
#    - min_price, max_price optional, ge=0
#    - Validate max_price >= min_price nếu cả 2 có
#      (gợi ý: @model_validator, học ở 03_pydantic.py)
#
# 2. Thêm POST /products với schema:
#    - name (required, min 2, max 100)
#    - price (required, > 0)
#    - tags (list[str], default [])
#    - description (optional)
#
# 3. Thêm DELETE /products/{id} status_code 204
#
# 4. Thử gửi request SAI (age âm, email xấu, name quá ngắn) qua /docs
#    → quan sát 422 error message FastAPI tự trả về


# === Ghi chú quan trọng ===
#
# - Annotated[Type, Query/Path/Body(...)] — pattern chuẩn của FastAPI hiện đại
# - response_model filter output, kể cả khi code trả về field thừa
# - exclude_unset=True cho PATCH: chỉ lấy field user gửi, bỏ qua default
# - 422 = validation error (FastAPI tự)
# - 400 = business logic error (mình raise HTTPException)
