# Phase 2 — FastAPI Basics

**Thời gian:** 5-7 ngày
**Mục tiêu:** Viết được API đầy đủ CRUD (in-memory) với FastAPI + Pydantic V2.

## Bạn sẽ học được gì

- FastAPI app setup, uvicorn
- Path parameter, query parameter, request body
- Pydantic V2: schema, validation, custom validator
- Response model (kiểm soát output)
- Status code, HTTPException
- `APIRouter` (chia module)
- Dependency injection (`Depends`)
- Swagger UI / ReDoc / OpenAPI
- Middleware, CORS
- Background tasks

## Pattern nền tảng bạn sẽ lặp đi lặp lại

```
Request → Pydantic (validate input) → Business logic → Pydantic (format output) → Response
```

## Kế hoạch

| Ngày | Chủ đề | File |
|------|--------|------|
| 1 | Hello world, Swagger UI | `01_hello.py` |
| 2 | Path/Query/Body, Pydantic | `02_params.py` |
| 3 | Pydantic V2 validation sâu | `03_pydantic.py` |
| 4 | Router, Depends | `04_dependencies.py` |
| 5 | Error handling, middleware | `05_errors.py` |
| 6-7 | Mini-project: Notes API | `mini-project/` |

## Setup project lần đầu

```bash
cd phase-2-fastapi-basics
uv init
uv add "fastapi[standard]" pydantic
uv add --dev pytest httpx ruff mypy
```

Chạy dev server:
```bash
uv run fastapi dev 01_hello.py
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs     (Swagger UI)
# → http://127.0.0.1:8000/redoc    (ReDoc)
```

## Quy tắc quan trọng

### ✅ DO
- **Luôn dùng Pydantic model cho request body** (không dùng `dict`)
- **Luôn khai báo `response_model`** (tránh leak field nhạy cảm)
- **`Annotated` cho mọi dependency** — không dùng `param: X = Depends(...)`
- **`async def` cho endpoint có I/O**
- **Tách router theo resource** (users, posts, ...) ngay từ đầu

### ❌ DON'T
- ❌ Dùng Pydantic V1 syntax (`@validator`, `class Config`)
- ❌ Trả về object ORM trực tiếp không qua response_model
- ❌ Hardcode config trong code — dùng `pydantic-settings`
- ❌ Catch Exception chung chung — bắt cụ thể, raise HTTPException

## Mini-project: Notes API (in-memory)

REST API quản lý ghi chú, lưu trong dict (chưa có DB).

```
GET    /notes                 # list (có pagination, filter by tag)
POST   /notes                 # tạo
GET    /notes/{id}            # xem
PATCH  /notes/{id}            # cập nhật
DELETE /notes/{id}            # xoá
GET    /notes/search?q=...    # tìm kiếm
```

Yêu cầu xem [mini-project/README.md](mini-project/README.md).

## Checklist trước Phase 3

- [ ] Tự viết được endpoint với path + query + body
- [ ] Hiểu Pydantic V2: `field_validator`, `model_validator`, `model_config`
- [ ] Dùng thành thạo `response_model`, `status_code`, `HTTPException`
- [ ] Biết dùng `Depends` + `Annotated`
- [ ] Tách project ra `routers/`, `schemas/`
- [ ] Swagger UI hiển thị đầy đủ schema, example
- [ ] Mini-project Notes chạy OK, tất cả endpoint test bằng Swagger UI

→ [Phase 3: Database với PostgreSQL](../phase-3-database/PHASE.md)
