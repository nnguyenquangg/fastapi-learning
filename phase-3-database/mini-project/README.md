# Mini-project: Blog API với PostgreSQL

Upgrade Notes API (Phase 2) → Blog API thực với DB.

## Feature

### Users
- Đăng ký (trong phase này chưa có password hashing thực - phase 4)
- Lấy profile
- Update profile

### Posts
- CRUD đầy đủ
- Filter by tag, by author
- Search full-text (title + content)
- Pagination
- Soft delete (không xoá thật, set `deleted_at`)

### Comments
- Thêm comment vào post
- List comment của post (pagination)
- Xoá comment (chỉ tác giả hoặc admin — phase 4 mới thật sự enforce)

### Tags
- Tạo tag
- Gán tag vào post
- List post theo tag

## Data model

```
┌──────┐ 1   N ┌──────┐
│ User │ ────▶│ Post │ ◀──┐ N
└──────┘       └──────┘    │ Tag (M:N)
    │ 1            │ 1     │
    │              │ N     │
    │          ┌─────────┐ │
    └─────────▶│ Comment │─┘
         N     └─────────┘
```

Schema chi tiết:

```python
class User:
    id, email (unique), name, hashed_password, is_active,
    created_at, updated_at

class Post:
    id, title, slug (unique), content, author_id (→User),
    is_published, published_at, deleted_at,
    created_at, updated_at

class Tag:
    id, name (unique), slug (unique)

class PostTag:  # association
    post_id, tag_id, (PK composite)

class Comment:
    id, post_id (→Post), author_id (→User), content,
    created_at, updated_at
```

## Cấu trúc project

```
mini-project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py              # Settings (pydantic-settings)
│   ├── db.py                  # engine, SessionLocal, get_db
│   ├── models/
│   │   ├── __init__.py        # import để Alembic thấy
│   │   ├── base.py            # Base, TimestampMixin
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── comment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── comment.py
│   ├── repositories/
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── comment.py
│   ├── services/
│   │   ├── user.py
│   │   ├── post.py
│   │   └── comment.py
│   ├── routers/
│   │   ├── users.py
│   │   ├── posts.py
│   │   ├── tags.py
│   │   └── comments.py
│   └── dependencies.py
├── migrations/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py            # fixtures: test db, client
│   └── test_posts.py
├── alembic.ini
├── .env.example
└── pyproject.toml
```

## Setup

```bash
cd mini-project
uv init
uv add "fastapi[standard]" pydantic pydantic-settings \
    "sqlalchemy[asyncio]" asyncpg alembic
uv add --dev pytest pytest-asyncio httpx ruff mypy

# DB riêng cho project
docker exec -it learn-pg psql -U postgres -c "CREATE DATABASE blog_api;"

# .env
cat > .env <<EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/blog_api
ECHO_SQL=false
EOF

# Alembic init
uv run alembic init -t async migrations
# → sửa env.py như đã hướng dẫn ở 03_alembic.md
```

## Checklist thực hiện

### Step 1: Foundation
- [ ] Settings + engine + session + get_db
- [ ] Base, TimestampMixin
- [ ] Model User
- [ ] Alembic migration 1: tạo bảng users
- [ ] Router + schema + service + repo cho User CRUD (không auth)
- [ ] Swagger test OK

### Step 2: Posts + Tags
- [ ] Model Post, Tag, PostTag (association table)
- [ ] Migration 2: thêm các bảng
- [ ] CRUD Post
- [ ] Slug auto từ title (có validator tránh trùng)
- [ ] Tag CRUD + gán tag vào post
- [ ] Filter post: by tag, by author, by is_published

### Step 3: Comments
- [ ] Model Comment
- [ ] Migration 3
- [ ] POST /posts/{id}/comments
- [ ] GET /posts/{id}/comments (pagination)
- [ ] DELETE /comments/{id}

### Step 4: Search + Polish
- [ ] GET /posts/search?q=... (ILIKE trên title + content)
- [ ] Soft delete cho Post (đặt deleted_at, exclude khỏi query default)
- [ ] Eager load: list post → kèm author name, tags, comment count
- [ ] Confirm không N+1 (bật echo, đếm query)

### Step 5: Tests
- [ ] conftest fixture: test DB riêng, rollback sau mỗi test
- [ ] Test happy path CRUD User, Post, Comment
- [ ] Test error: 404, 409, 422

### Step 6: Bonus
- [ ] `GET /posts/{slug}` bằng slug thay cho id
- [ ] Response có field `comment_count` (count subquery)
- [ ] Rate limit basic (tự middleware đếm request/IP)

## Tips

- **Bật `echo=True`** trong dev → thấy mọi SQL → debug N+1 nhanh
- **Dùng TablePlus/DBeaver** để inspect data khi debug
- **Commit sau mỗi step** — không cần hoàn hảo, cần chạy được
- **Đừng code tất cả rồi mới chạy** — mỗi lần thêm 1 endpoint, test ngay

## Deploy (bonus)

- [Railway](https://railway.app) cho cả app + Postgres (free tier)
- `Dockerfile` + `docker-compose.yml` cho local parity

Xong → [Phase 4: Auth & Security](../../phase-4-auth-security/PHASE.md)
