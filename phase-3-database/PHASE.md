# Phase 3 — PostgreSQL + SQLAlchemy Async

**Thời gian:** 7-10 ngày
**Mục tiêu:** Backend thật với DB, hiểu được ORM async, migration, relationship.

## Bạn sẽ học được gì

- SQL cơ bản (trực tiếp trên PostgreSQL)
- SQLAlchemy 2.0 async ORM
- Declarative model với `Mapped` annotation
- Alembic migration (tạo/sửa/xoá table có version)
- Relationship: One-to-many, Many-to-many, One-to-one
- Eager vs lazy loading (tránh N+1)
- `AsyncSession`, transaction, rollback
- Session dependency pattern trong FastAPI
- Pagination, filter, sort trên DB

## Bắt đầu bằng SQL thuần (bắt buộc!)

Đừng nhảy thẳng vào ORM. **Ngày 1-2 dùng psql hoặc GUI để viết SQL tay** — sau này debug query chậm mới hiểu được ORM đang gì.

## Kế hoạch

| Ngày | Chủ đề | File |
|------|--------|------|
| 1 | SQL cơ bản: CREATE, INSERT, SELECT, WHERE | `sql/01_basics.sql` |
| 2 | JOIN, GROUP BY, subquery, index | `sql/02_joins.sql` |
| 3 | Connect FastAPI với asyncpg + SQLAlchemy | `examples/01_connection.py` |
| 4 | Model + basic CRUD | `examples/02_crud.py` |
| 5 | Alembic migration | `examples/03_alembic.md` |
| 6 | Relationship + eager loading | `examples/04_relationships.py` |
| 7 | Transaction, unit of work | `examples/05_transactions.py` |
| 8-10 | Mini-project: Blog API | `mini-project/` |

## Kiến trúc layer (học ngay từ bây giờ)

```
┌──────────────────┐
│  Router layer    │   # FastAPI endpoint - parse request, gọi service
├──────────────────┤
│  Service layer   │   # Business logic - orchestrate
├──────────────────┤
│  Repository/CRUD │   # DB query thô - nhận AsyncSession, return model
├──────────────────┤
│  Model (ORM)     │   # SQLAlchemy declarative
└──────────────────┘
```

Không trộn SQL query vào endpoint. Bạn sẽ cảm ơn bản thân sau 2 tháng.

## Setup PostgreSQL cho phase này

```bash
# Tạo database riêng cho phase 3
docker exec -it learn-pg psql -U postgres -c "CREATE DATABASE phase3;"

# Connect
docker exec -it learn-pg psql -U postgres -d phase3
```

Environment variable:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/phase3
```

## Package cần cài

```bash
uv add sqlalchemy[asyncio] asyncpg alembic pydantic-settings
```

## Quy tắc vàng của async SQLAlchemy

### ✅ DO
- Luôn dùng `async with session` hoặc `get_db` dependency
- `await session.commit()` sau khi modify
- `await session.refresh(obj)` sau create nếu cần id từ DB
- Dùng `selectinload` / `joinedload` để tránh N+1
- Dùng `session.scalars(stmt).all()` thay `session.execute(stmt).all()` khi query 1 entity

### ❌ DON'T
- ❌ Dùng `psycopg2` (sync driver) trong async app
- ❌ Dùng lazy loading (`relationship()` default) trong async mà không eager → lỗi `MissingGreenlet`
- ❌ Tạo session global - mỗi request một session
- ❌ Commit nhiều lần trong 1 request - 1 transaction = 1 commit

## Mini-project: Blog API

Upgrade Notes API → Blog API với PostgreSQL thật:
- User (author)
- Post (thuộc về User, có tags many-to-many)
- Comment (thuộc về User và Post)
- Tag

Xem [mini-project/README.md](mini-project/README.md).

## Checklist trước Phase 4

- [ ] Viết được SQL query có JOIN từ đầu
- [ ] Hiểu sự khác biệt INNER JOIN vs LEFT JOIN
- [ ] Đọc được `EXPLAIN` output cơ bản
- [ ] Tạo model với `Mapped[...]` và relationship đúng
- [ ] Alembic: tạo migration, `upgrade`, `downgrade` thành thạo
- [ ] Không còn lỗi N+1 (dùng `selectinload`)
- [ ] Pattern repository/service hoạt động
- [ ] Test được với test DB riêng (transaction rollback sau test)

→ [Phase 4: Authentication & Security](../phase-4-auth-security/PHASE.md)
