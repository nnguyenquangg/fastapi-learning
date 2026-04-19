# Alembic Migration — Hướng Dẫn

## Tại sao cần Alembic?

Không có Alembic:
- Thêm column → phải nhớ chạy ALTER TABLE tay trên mọi môi trường (dev, staging, prod)
- Ai vào sau không biết schema hiện tại là gì
- Rollback? Không có cửa

Có Alembic:
- Mỗi thay đổi schema = 1 file migration có version
- Chạy `alembic upgrade head` → đồng bộ mọi nơi
- `alembic downgrade -1` để undo
- `alembic history` xem lịch sử

## Setup

```bash
cd your-project
uv add alembic

# Init scaffold
uv run alembic init -t async migrations
```

Cấu trúc được tạo:
```
migrations/
├── env.py              # config runtime
├── script.py.mako      # template cho migration
└── versions/           # các file migration
alembic.ini             # config
```

## Cấu hình

### 1. `alembic.ini`

Không cần thay đổi nhiều. Quan trọng là **bỏ** `sqlalchemy.url` hardcoded (sẽ lấy từ env).

### 2. `migrations/env.py`

Chỉnh để:
- Đọc `DATABASE_URL` từ env / settings
- Import `Base.metadata` để Alembic biết model của bạn

```python
# migrations/env.py (phần quan trọng)
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.db import Base           # ← import Base class
from app import models            # ← QUAN TRỌNG: import để Base biết các model
from app.config import get_settings


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,         # detect khi đổi type column
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


run_migrations_online()
```

## Workflow hàng ngày

### Tạo migration từ thay đổi model (autogenerate)

```bash
# 1. Sửa model (vd thêm column)
# 2. Generate migration:
uv run alembic revision --autogenerate -m "add bio to users"

# 3. KIỂM TRA file migrations/versions/xxx_add_bio_to_users.py
#    — autogenerate KHÔNG hoàn hảo, luôn review
# 4. Áp dụng:
uv run alembic upgrade head
```

### Tạo migration thủ công (khuyến khích khi phức tạp)

```bash
uv run alembic revision -m "backfill user slugs"
```

Rồi sửa `upgrade()` và `downgrade()` thủ công.

### Xem trạng thái

```bash
uv run alembic current       # version hiện tại của DB
uv run alembic history       # lịch sử migration
uv run alembic show head     # chi tiết migration mới nhất
```

### Rollback

```bash
uv run alembic downgrade -1          # lùi 1 bước
uv run alembic downgrade base        # về trạng thái đầu
uv run alembic downgrade <rev_id>    # về version cụ thể
```

### Generate SQL (review trước khi chạy)

```bash
uv run alembic upgrade head --sql    # xuất SQL, không chạy
```

## Ví dụ migration (đọc để quen)

```python
"""add bio to users

Revision ID: a1b2c3d4
Revises: 7f8e9d2c
Create Date: 2025-04-19 10:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4"
down_revision = "7f8e9d2c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("bio", sa.String(500), nullable=True))
    op.create_index("ix_users_name", "users", ["name"])


def downgrade() -> None:
    op.drop_index("ix_users_name", table_name="users")
    op.drop_column("users", "bio")
```

## Quy tắc vàng

### ✅ DO
- **Luôn review** file autogenerate, Alembic hay bỏ sót
- **Viết downgrade cùng lúc** — giữ khả năng rollback
- **Migration = commit** — không sửa migration đã merge/deploy
- **Data migration** tách riêng với schema migration nếu có thể
- **Test** migration trên DB staging trước production

### ❌ DON'T
- ❌ Sửa file migration sau khi đã chạy trên staging/prod
- ❌ Autogenerate rồi áp dụng mù, không đọc
- ❌ Drop column chứa data quan trọng trong 1 lần deploy — làm 2 bước:
  1. Release 1: ngừng ghi vào column
  2. Release 2: mới drop
- ❌ Dùng Python logic nặng trong migration — giữ migration deterministic

## Khi autogenerate KHÔNG bắt được

- Thay đổi `CheckConstraint` name
- Đổi tên column (autogenerate sẽ thấy drop + add, mất data!) → sửa tay `op.alter_column(..., new_column_name=...)`
- `server_default` phức tạp
- Partition table
- Extension (`CREATE EXTENSION`)

## Tips debug

- `alembic revision --autogenerate --sql` → xem migration dự kiến không chạy
- Nếu generate ra file trống → check `env.py` đã import model chưa
- Multiple heads (2 branch migration song song) → dùng `alembic merge`

## Bài tập

1. Tạo project mini với 1 model `User`. Setup Alembic, `upgrade head`
2. Thêm column `bio`, autogenerate migration, kiểm tra file, upgrade
3. Đổi tên column `bio` → `description`. **Tự viết** migration (không autogenerate)
4. Thêm model `Post` với relationship tới User. Autogenerate migration
5. Rollback 2 bước, upgrade lại
6. Tạo data migration: INSERT 3 tag mặc định vào bảng tags

Xong → `04_relationships.py`
