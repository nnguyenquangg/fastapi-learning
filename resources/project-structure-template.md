# Project Structure Template

Cấu trúc đề xuất cho FastAPI project production.

## Phiên bản đơn giản (monolith nhỏ)

Phù hợp project < 20 endpoint, 1-2 developer.

```
my-app/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI() + include routers
│   ├── config.py                # Settings
│   ├── db.py                    # engine, SessionLocal, get_db
│   ├── dependencies.py          # common deps (auth, pagination)
│   ├── exceptions.py            # custom exceptions + handlers
│   ├── models.py                # All SQLAlchemy models
│   ├── schemas.py               # All Pydantic schemas
│   ├── crud.py                  # DB queries (simple project)
│   ├── security.py              # hash, jwt
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       ├── users.py
│       └── items.py
├── migrations/
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```

## Phiên bản domain-split (monolith vừa)

Phù hợp project 20-100 endpoint, 3-6 developer.

```
my-app/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── exceptions.py
│   ├── middleware/
│   │   ├── request_id.py
│   │   ├── logging.py
│   │   └── security_headers.py
│   ├── security/
│   │   ├── password.py
│   │   ├── jwt.py
│   │   └── dependencies.py
│   ├── auth/                    # domain: authentication
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── dependencies.py
│   ├── users/                   # domain: user management
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── model.py             # nếu chỉ 1 model
│   │   ├── repository.py
│   │   └── service.py
│   ├── posts/                   # domain: posts
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── service.py
│   └── shared/
│       ├── base_model.py
│       ├── mixins.py
│       └── utils.py
├── migrations/
├── tests/
│   ├── conftest.py
│   ├── helpers.py
│   ├── factories.py
│   ├── unit/
│   └── integration/
├── scripts/
│   └── seed.py
├── docker/
│   └── Dockerfile
├── .github/workflows/ci.yml
└── ...
```

## Phiên bản layered (complex domain)

Khi có business logic phức tạp, muốn giảm coupling.

```
app/
├── api/                         # HTTP layer
│   ├── v1/
│   │   ├── routes/
│   │   └── dependencies/
│   └── main.py
├── application/                 # use case / service
│   ├── commands/                # write operations
│   ├── queries/                 # read operations
│   └── services/
├── domain/                      # business models (pure Python)
│   ├── entities/
│   ├── value_objects/
│   └── events/
├── infrastructure/              # DB, cache, email...
│   ├── db/
│   │   ├── models/              # SQLAlchemy ORM
│   │   └── repositories/
│   ├── cache/
│   ├── email/
│   └── storage/
└── config.py
```

⚠ Chỉ dùng structure này nếu:
- Team ≥ 5 người
- Domain logic thực sự phức tạp
- Kế hoạch dài hạn, tài nguyên duy trì

Nếu chưa chắc → dùng phiên bản domain-split. Refactor sau dễ hơn over-engineer từ đầu.

## Files nên có ở root

### `.env.example`
```bash
# App
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=change-me-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=replace-with-32-bytes-random
JWT_ACCESS_TTL_MINUTES=30
JWT_REFRESH_TTL_DAYS=14

# Email (optional)
SMTP_HOST=
SMTP_USER=
SMTP_PASS=

# Observability
SENTRY_DSN=
```

### `.gitignore`
```
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.env
.env.*
!.env.example
.pytest_cache/
.ruff_cache/
.mypy_cache/
htmlcov/
.coverage
*.db
*.sqlite
logs/
.DS_Store
.vscode/
.idea/
```

### `pyproject.toml` (uv)
```toml
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi[standard]>=0.115",
    "pydantic>=2.7",
    "pydantic-settings>=2.0",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "passlib[bcrypt]>=1.7",
    "python-jose[cryptography]>=3.3",
    "python-multipart>=0.0.9",
    "redis>=5.0",
    "structlog>=24.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5.0",
    "httpx>=0.27",
    "ruff>=0.4",
    "mypy>=1.10",
    "factory-boy>=3.3",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.coverage.run]
branch = true
source = ["app"]
omit = ["app/migrations/*"]
```

### `README.md` template
```markdown
# My App

One-line description.

![CI](link) ![Coverage](link)

## Features
- Feature 1
- Feature 2

## Tech Stack
- Python 3.12 + FastAPI
- PostgreSQL + SQLAlchemy 2.0 (async) + Alembic
- Redis
- Docker

## Quick Start

### Prerequisites
- Python 3.12
- Docker + Docker Compose

### Run locally
```bash
cp .env.example .env
docker compose up -d db redis
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

### Run tests
```bash
uv run pytest
```

## API Docs
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md)

## License
MIT
```

## Quy tắc tổ chức

### ✅ DO
- Tổ chức theo **feature/domain** (users/, posts/), không phải theo technical layer (models/, controllers/)
- Model ORM ở gần domain của nó
- Test mirror cấu trúc source (`app/users/` → `tests/users/`)
- Shared code ở `shared/` hoặc `common/`

### ❌ DON'T
- 1 file `models.py` 3000 dòng
- 1 thư mục `routers/` với 50 file không nhóm
- Import vòng (A imports B, B imports A) — refactor ngay
- Business logic trong router — tách sang service

## Khi nào refactor structure?

Nếu trả lời "có" cho ≥ 2 câu:
- Một file > 500 dòng?
- Gõ tên file/hàm mà phải nghĩ 5 giây mới nhớ ở đâu?
- Thêm feature mới phải sửa nhiều file khác nhau ở nhiều chỗ?
- 2 feature không liên quan dùng chung 1 file?

→ Refactor.
