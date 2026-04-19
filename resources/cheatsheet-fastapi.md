# FastAPI Cheatsheet

## Path, Query, Body

```python
from typing import Annotated
from fastapi import Path, Query, Body

@app.get("/items/{id}")
async def get(
    id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(min_length=2)] = None,
):
    ...

@app.post("/items")
async def create(
    payload: Annotated[ItemCreate, Body()],
):
    ...
```

## Dependency injection

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as s:
        yield s

DbDep = Annotated[AsyncSession, Depends(get_db)]

@app.get("/items/{id}")
async def handler(id: int, db: DbDep): ...
```

## Status codes thường dùng

| Code | Ý nghĩa | Khi nào |
|------|---------|---------|
| 200  | OK | GET thành công, update thành công |
| 201  | Created | POST tạo mới thành công |
| 204  | No Content | DELETE, update không trả body |
| 400  | Bad Request | Business logic sai (VD số dư không đủ) |
| 401  | Unauthorized | Chưa login hoặc token sai |
| 403  | Forbidden | Đã login nhưng không có quyền |
| 404  | Not Found | Resource không tồn tại |
| 409  | Conflict | Duplicate (email trùng, concurrent edit) |
| 422  | Unprocessable | Pydantic validation fail (tự động) |
| 429  | Too Many Requests | Rate limit |
| 500  | Internal Error | Bug server |
| 503  | Service Unavailable | DB/downstream down |

## HTTPException

```python
raise HTTPException(
    status_code=404,
    detail="User not found",
    headers={"X-Error": "user-not-found"},   # optional
)
```

## Response model filter

```python
class UserRead(BaseModel):
    id: int
    email: str
    # Không có hashed_password → không leak

@app.get("/users/{id}", response_model=UserRead)
async def get_user(id: int) -> User:   # return ORM object
    ...   # FastAPI filter theo UserRead
```

## Common patterns

### Pagination dependency
```python
class Pagination(BaseModel):
    page: int
    size: int
    offset: int

async def pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Pagination:
    return Pagination(page=page, size=size, offset=(page - 1) * size)

PageDep = Annotated[Pagination, Depends(pagination)]
```

### Optional current user
```python
async def get_current_user_optional(
    authorization: Annotated[str | None, Header()] = None,
) -> User | None:
    if not authorization:
        return None
    try:
        return await _decode(authorization)
    except Exception:
        return None
```

### APIRouter với prefix
```python
router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    dependencies=[Depends(some_common_dep)],   # áp tất cả endpoint
    responses={404: {"description": "Not found"}},
)
```

## Chạy uvicorn

```bash
# Dev (auto-reload)
uv run fastapi dev app/main.py

# Prod
uv run uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 \
    --workers 4 \
    --proxy-headers --forwarded-allow-ips='*'
```

## Logging request trong middleware

```python
@app.middleware("http")
async def log(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    logger.info("%s %s %s %.3fs",
                request.method, request.url.path,
                response.status_code, duration)
    return response
```

## CORS (dev vs prod)

```python
# Dev
allow_origins=["http://localhost:5173"]
# Prod
allow_origins=["https://yourdomain.com"]
# ❌ ["*"] khi allow_credentials=True
```

## File upload

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg"):
        raise HTTPException(400, "Only png/jpg")
    content = await file.read()
    # Lưu
    ...
```

## WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        ...
```

## Common errors & fix

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `MissingGreenlet` | Access lazy attribute trong async | Dùng `selectinload`/`joinedload` |
| `422 Unprocessable` | Pydantic validation fail | Check body JSON, field type |
| `405 Method Not Allowed` | Path đúng nhưng method sai | Check `@app.get` vs `@app.post` |
| `307 Redirect` | Path có/không trailing slash | FastAPI redirect `/items` → `/items/` |
| `IntegrityError` | Unique/FK constraint | Handle 409 Conflict explicit |
| `Body field required` | Thiếu `Annotated[..., Body()]` khi 1 field đơn | Dùng Pydantic model thay vì raw type |

## Docs customization

```python
app = FastAPI(
    title="My API",
    description="...",
    version="1.0.0",
    docs_url="/docs",           # None để tắt
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Authentication"},
        {"name": "users", "description": "User CRUD"},
    ],
)
```

## Tắt docs trong production (nếu cần)

```python
app = FastAPI(
    docs_url=None if settings.environment == "production" else "/docs",
)
```
