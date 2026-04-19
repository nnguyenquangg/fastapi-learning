"""
Example 02 — Test FastAPI Endpoint với httpx AsyncClient

Hai cách:
1. TestClient (sync) - đơn giản, đủ cho hầu hết case
2. httpx.AsyncClient - khi endpoint dùng async dependency nội bộ
   (kết nối DB thật, fixture async...)

Khuyến nghị: dùng AsyncClient với ASGITransport - match với production flow.
"""
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel


# ============================================================
# App ví dụ
# ============================================================
class Item(BaseModel):
    id: int
    name: str


ITEMS: dict[int, Item] = {}
_NEXT_ID = 1


def get_items_db() -> dict[int, Item]:
    """Dependency có thể override trong test."""
    return ITEMS


ItemsDbDep = Annotated[dict[int, Item], Depends(get_items_db)]


app = FastAPI()


@app.post("/items", response_model=Item, status_code=201)
async def create_item(name: str, db: ItemsDbDep) -> Item:
    global _NEXT_ID
    item = Item(id=_NEXT_ID, name=name)
    db[_NEXT_ID] = item
    _NEXT_ID += 1
    return item


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: ItemsDbDep) -> Item:
    if item_id not in db:
        raise HTTPException(404, "Not found")
    return db[item_id]


@app.get("/items", response_model=list[Item])
async def list_items(db: ItemsDbDep) -> list[Item]:
    return list(db.values())


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def clean_db():
    """Reset DB giữa các test."""
    global _NEXT_ID
    ITEMS.clear()
    _NEXT_ID = 1
    yield ITEMS


@pytest.fixture
async def client(clean_db):
    """AsyncClient gắn với app, không thật sự lên network."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ============================================================
# Tests
# ============================================================
async def test_create_item(client: AsyncClient):
    # Arrange
    # Act
    response = await client.post("/items", params={"name": "Book"})
    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Book"


async def test_get_item_not_found(client: AsyncClient):
    response = await client.get("/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}


async def test_list_items_empty(client: AsyncClient):
    response = await client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


async def test_full_crud_flow(client: AsyncClient):
    # Create 2 items
    await client.post("/items", params={"name": "A"})
    await client.post("/items", params={"name": "B"})

    # List
    response = await client.get("/items")
    items = response.json()
    assert len(items) == 2
    assert {i["name"] for i in items} == {"A", "B"}

    # Get one
    response = await client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "A"


# ============================================================
# Dependency override (thay dependency trong test)
# ============================================================
async def test_with_fake_db():
    """
    Override get_items_db bằng DB giả tự kiểm soát.
    Hữu ích khi muốn test behavior cụ thể mà không cần seed thật.
    """
    fake_db: dict[int, Item] = {
        100: Item(id=100, name="Only item"),
    }

    app.dependency_overrides[get_items_db] = lambda: fake_db

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            response = await c.get("/items/100")
            assert response.status_code == 200
            assert response.json() == {"id": 100, "name": "Only item"}

            response = await c.get("/items/1")   # id 1 không tồn tại trong fake_db
            assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


# ============================================================
# Parametrize endpoint test
# ============================================================
@pytest.mark.parametrize(
    "name,expected_status",
    [
        ("valid name", 201),
        ("", 201),         # chưa validate min length - nếu validate thì đổi 422
        ("A" * 1000, 201), # cũng vậy
    ],
)
async def test_create_item_various(client: AsyncClient, name: str, expected_status: int):
    response = await client.post("/items", params={"name": name})
    assert response.status_code == expected_status


# ============================================================
# Test body JSON
# ============================================================
class CreatePayload(BaseModel):
    name: str


@app.post("/v2/items", response_model=Item, status_code=201)
async def create_v2(payload: CreatePayload, db: ItemsDbDep) -> Item:
    global _NEXT_ID
    item = Item(id=_NEXT_ID, name=payload.name)
    db[_NEXT_ID] = item
    _NEXT_ID += 1
    return item


async def test_create_v2_validates_json(client: AsyncClient):
    # Thiếu field
    response = await client.post("/v2/items", json={})
    assert response.status_code == 422

    # Đúng
    response = await client.post("/v2/items", json={"name": "Valid"})
    assert response.status_code == 201


# ============================================================
# Bài tập
# ============================================================
#
# 1. App có endpoint PATCH /items/{id} update name.
#    Viết test:
#    - Happy path: update thành công → 200
#    - Not found: id không tồn tại → 404
#    - Validation: name rỗng → 422
#
# 2. App có endpoint DELETE /items/{id}.
#    - Test xoá xong gọi GET → 404
#    - Test xoá id không tồn tại → 404
#
# 3. Refactor fixture: tạo fixture `created_items` trả về list[Item]
#    đã pre-seed vào DB bằng POST. Dùng trong test nào cần data sẵn.
