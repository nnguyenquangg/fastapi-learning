# Mini-project: Notes API (in-memory)

REST API quản lý ghi chú. **Chưa có DB** - lưu trong dict. Phase 3 sẽ migrate sang PostgreSQL.

## Endpoints

```
GET    /notes                    # list notes, có pagination + filter tag
POST   /notes                    # tạo note
GET    /notes/{id}               # chi tiết note
PATCH  /notes/{id}               # cập nhật
DELETE /notes/{id}               # xoá
GET    /notes/search?q=...       # full-text search đơn giản trong title + content

GET    /health                   # health check
```

## Data model

```python
class Note(BaseModel):
    id: int
    title: str              # 2-200 ký tự
    content: str            # 1-5000 ký tự
    tags: list[str]         # tối đa 10, mỗi tag 2-20 ký tự, lowercase
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime
```

## Cấu trúc project

```
mini-project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, include routers
│   ├── schemas.py              # Pydantic models (NoteCreate, NoteUpdate, NoteRead)
│   ├── storage.py              # Fake in-memory DB (dict) - class NoteStorage
│   ├── dependencies.py         # get_storage, pagination_params...
│   └── routers/
│       ├── __init__.py
│       └── notes.py            # CRUD endpoints
├── tests/
│   └── test_notes.py           # pytest + httpx
├── pyproject.toml
└── README.md
```

## Setup

```bash
cd mini-project
uv init
uv add "fastapi[standard]" pydantic
uv add --dev pytest pytest-asyncio httpx ruff mypy

uv run fastapi dev app/main.py
```

## Yêu cầu chi tiết

### 1. Pydantic schemas
- `NoteBase` (title, content, tags, is_pinned)
- `NoteCreate(NoteBase)` — input POST
- `NoteUpdate` — tất cả optional, dùng cho PATCH
- `NoteRead(NoteBase)` — output, thêm id + timestamps
- `NotesPage` — list response: `{items: list[NoteRead], total: int, page: int, size: int}`
- Validator:
  - Tags: lowercase, không trùng, pattern `^[a-z0-9-]+$`
  - Title/content: strip whitespace

### 2. Storage layer
```python
class NoteStorage:
    def __init__(self) -> None: ...
    async def list(self, *, tag: str | None, page: int, size: int) -> tuple[list[Note], int]: ...
    async def get(self, note_id: int) -> Note | None: ...
    async def create(self, data: NoteCreate) -> Note: ...
    async def update(self, note_id: int, data: NoteUpdate) -> Note | None: ...
    async def delete(self, note_id: int) -> bool: ...
    async def search(self, query: str) -> list[Note]: ...
```
Trong memory chỉ cần `dict[int, Note]` + counter cho id.

### 3. Dependency injection
- Singleton storage (có thể dùng module-level instance hoặc `lru_cache`)
- `PaginationDep` với `page>=1, size in [1, 100]`

### 4. Error handling
- GET/PATCH/DELETE trên id không tồn tại → 404 với custom message
- Validation lỗi → 422 (tự động)
- Bonus: custom exception handler cho `NoteNotFoundError`

### 5. Tests (bonus mạnh, làm luôn)
- Dùng `TestClient` từ `fastapi.testclient` (hoặc `httpx.AsyncClient`)
- Test happy path + error path cho mỗi endpoint
- Reset storage trước mỗi test (fixture)

## Checklist

- [ ] Tất cả endpoint hoạt động qua Swagger UI
- [ ] Validation thấy đủ trong `/docs`
- [ ] Tags bị chuyển về lowercase
- [ ] Pagination đúng (page=2, size=5 → items 6-10)
- [ ] Search không case-sensitive
- [ ] 404 khi id không tồn tại
- [ ] Đã có ít nhất 3-5 test pass
- [ ] `ruff check .` sạch
- [ ] `mypy app/` pass

## Sau khi xong

- Commit code
- Deploy thử lên [Railway](https://railway.app) hoặc [Fly.io](https://fly.io) (free tier) — bonus
- Sang [Phase 3](../../phase-3-database/PHASE.md): thay in-memory storage bằng PostgreSQL
