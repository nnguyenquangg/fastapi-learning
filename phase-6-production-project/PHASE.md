# Phase 6 — Production-Ready Project

**Thời gian:** 2-3 tuần
**Mục tiêu:** Build 1 app backend đầy đủ tính năng + deploy thật + có observability.

## Chọn 1 trong 3 project

Ưu tiên chọn project bạn **thực sự muốn dùng** hoặc **giải quyết vấn đề cá nhân** — motivation >> tutorial.

### Option A: Task Manager API (khuyến khích nếu mới)
- User, Workspace, Project, Task, Assignee, Comment, Attachment
- Tính năng: drag-drop status, filter, deadline, notify khi gần deadline
- Mức: Trung bình
- Học được: nhiều relationship, background task, email notification

### Option B: Marketplace / E-commerce
- User, Product, Category, Cart, Order, Payment (stripe test mode)
- Tính năng: checkout flow, webhook payment, stock management, invoice PDF
- Mức: Cao
- Học được: transaction phức tạp, webhook, PDF generation, file upload

### Option C: Content Platform (Medium-clone)
- User, Post, Comment, Follow, Like, Bookmark, Tag, Feed
- Tính năng: timeline cá nhân, search, image upload (S3), notification
- Mức: Trung bình
- Học được: feed algorithm, full-text search, S3 upload, notification

## Yêu cầu chung (bắt buộc)

### Core feature
- [ ] Auth đầy đủ (register, login, refresh, logout, change password)
- [ ] Email verification hoặc magic link (tùy chọn)
- [ ] RBAC: user/admin, có thể thêm role theo project
- [ ] Profile: update info, avatar upload

### Kỹ thuật
- [ ] PostgreSQL + SQLAlchemy async + Alembic migration
- [ ] Redis (cache + rate limit + session nếu cần)
- [ ] Background job với **Taskiq** hoặc **arq** (async-native)
  - Email notification
  - Xử lý file nặng
  - Scheduled task (daily report, cleanup)
- [ ] File upload (local or S3-compat như MinIO)
- [ ] Search (basic: `ILIKE` / Postgres full-text; advanced: Meilisearch/Typesense)
- [ ] Rate limiting production-grade (slowapi + Redis)
- [ ] Structured logging (JSON, có request_id)
- [ ] Health check: `/health` + `/health/ready` (k8s-style)
- [ ] Metrics: Prometheus endpoint `/metrics`
- [ ] OpenAPI docs đầy đủ (tag, description, example)

### Testing
- [ ] Coverage ≥ 80%
- [ ] Tests/phase 5 pattern
- [ ] Smoke test E2E cho 1-2 critical flow

### DevOps
- [ ] `Dockerfile` multi-stage, tối ưu size
- [ ] `docker-compose.yml` cho local dev (app + postgres + redis)
- [ ] `.env.example` có sẵn, README hướng dẫn
- [ ] GitHub Actions CI: lint + type + test + build image
- [ ] Deploy thật lên: Railway/Fly.io/Render/Cloud Run (có domain HTTPS)
- [ ] Observability: Sentry cho error, Grafana Cloud hoặc Better Stack cho log

### Documentation
- [ ] README.md: screenshot, feature list, setup guide
- [ ] ARCHITECTURE.md: sơ đồ component + flow chính
- [ ] API.md hoặc Postman collection (bonus)
- [ ] CHANGELOG.md

## Cấu trúc project production (tham khảo)

```
my-app/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI(), include routers, lifespan
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── db.py                      # engine, session, get_db
│   ├── cache.py                   # redis client
│   ├── logging_config.py          # structlog setup
│   ├── exceptions.py              # custom exceptions + handlers
│   ├── middleware/
│   │   ├── request_id.py          # add X-Request-ID
│   │   ├── logging.py             # log mỗi request
│   │   ├── rate_limit.py
│   │   └── security_headers.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   └── ...
│   ├── schemas/
│   │   ├── user.py
│   │   └── ...
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── ...
│   ├── tasks/                     # background jobs (taskiq)
│   │   ├── broker.py
│   │   ├── email.py
│   │   └── scheduled.py
│   ├── security/
│   │   ├── password.py
│   │   ├── jwt.py
│   │   └── dependencies.py
│   ├── events/                    # domain events (nếu dùng)
│   └── storage/                   # file storage (S3 adapter)
├── migrations/
│   ├── env.py
│   └── versions/
├── tests/
├── scripts/
│   ├── seed.py                    # tạo admin, sample data
│   └── healthcheck.py
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md
└── CHANGELOG.md
```

## Lộ trình gợi ý 3 tuần

### Tuần 1: Foundation
- Ngày 1-2: Setup project skeleton, Docker compose, migration đầu tiên
- Ngày 3-4: Auth đầy đủ (có test)
- Ngày 5-7: Core models + CRUD + test

### Tuần 2: Features + Polish
- Ngày 8-10: Feature phức tạp (upload file, background email, search)
- Ngày 11-12: Observability (log, metric, Sentry)
- Ngày 13-14: Test đạt 80% coverage, lint sạch

### Tuần 3: Deploy + Iterate
- Ngày 15-17: Dockerfile production, CI pipeline, deploy Railway/Fly.io
- Ngày 18-19: Load test nhỏ, optimize query chậm nhất
- Ngày 20-21: Documentation, demo video, chia sẻ lên LinkedIn/Twitter

## Dockerfile mẫu (multi-stage)

```dockerfile
# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
RUN useradd -m -u 1000 app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

## docker-compose.yml mẫu

```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/app
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: dev-secret-replace-me-32-chars-xxxx
    depends_on:
      db: {condition: service_healthy}
      redis: {condition: service_started}
    volumes:
      - ./app:/app/app

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  worker:
    build: .
    command: taskiq worker app.tasks.broker:broker --reload
    environment: *app-env   # share env với app
    depends_on: [db, redis]

volumes:
  pgdata:
```

## Deploy production

### Railway (đơn giản nhất)
1. Connect GitHub repo
2. Add Postgres + Redis plugin
3. Env vars từ `.env.example`
4. Auto deploy on push

### Fly.io (control nhiều hơn)
1. `fly launch` → tạo app
2. `fly postgres create` → tạo DB
3. `fly redis create` (hoặc Upstash)
4. `fly deploy`

### Bất kỳ provider nào
- Chạy migration trước khi start app: entrypoint script `alembic upgrade head && uvicorn ...`
- Set env var đúng, đặc biệt JWT_SECRET và DATABASE_URL
- Health check endpoint hook vào platform
- Logs → JSON → parse được bởi platform

## Criteria "xong"

- [ ] App deploy thật, có URL HTTPS công khai
- [ ] Ai cũng có thể dùng (register + demo flow)
- [ ] GitHub repo public, README có screenshot + demo link
- [ ] CI xanh
- [ ] Coverage badge ≥ 80%
- [ ] Bạn tự tin trả lời được những câu:
  - "Nếu 10k user cùng dùng thì sao?"
  - "Nếu DB down giữa chừng thì sao?"
  - "Làm sao bạn biết app đang chậm?"
  - "Bug xảy ra ở production, bạn debug thế nào?"

## Sau khi xong

- Viết bài blog chia sẻ → forcing function để hiểu sâu
- Làm thử thêm 1 project nhỏ để củng cố
- Học thêm: GraphQL (strawberry), WebSocket, gRPC, event-driven (Kafka)
- Tham gia open source FastAPI (fix bug, doc)

Chúc bạn build được nhiều thứ hay ho! 🚀
