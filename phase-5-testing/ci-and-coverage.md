# CI + Coverage

## Coverage cục bộ

```bash
# Chạy test + đo coverage
uv run pytest --cov=app --cov-report=term-missing --cov-report=html

# Xem HTML report
open htmlcov/index.html
```

Output term-missing:
```
Name                          Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
app/auth/routes.py               45      2     10      1    94%   23, 67
app/models/user.py               20      0      0      0   100%
---------------------------------------------------------------------
TOTAL                           200     12     30      3    92%
```

**Coverage mục tiêu:**
- Business logic: > 90%
- Endpoint: > 85%
- Overall project: > 80%

**Nhớ:** 100% coverage không có nghĩa là không có bug. Coverage chỉ là proxy, test chất lượng quan trọng hơn số.

## GitHub Actions CI

File `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: blog_api_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Lint
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Type check
        run: uv run mypy app

      - name: Run migrations
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/blog_api_test
          JWT_SECRET: test-secret-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        run: uv run alembic upgrade head

      - name: Test
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/blog_api_test
          JWT_SECRET: test-secret-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        run: |
          uv run pytest \
            --cov=app \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}
        if: github.event_name == 'push'
```

## Tips CI

### Chạy nhanh hơn
- **Cache uv**: `uses: astral-sh/setup-uv@v3` tự cache
- **Parallel test**: `pytest -n auto` (pytest-xdist)
- **Split suite**: unit tests chạy trước (< 10s), integration sau

### Fail-fast khi lint lỗi
- Đặt lint + type check TRƯỚC test
- Lỗi syntax/format → fail sớm, không cần chạy test chậm

### Secret trong CI
- Test: dùng secret fake (`test-secret-aaa...`) hardcode OK
- Production deploy: GitHub Secrets, không log ra console

### Matrix (test nhiều Python version)
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
steps:
  - run: uv python install ${{ matrix.python-version }}
```

## Badge README

```markdown
![CI](https://github.com/user/repo/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)
```

## Pre-commit hook (chạy lint local)

File `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Cài:
```bash
uv add --dev pre-commit
uv run pre-commit install
```

Mỗi lần `git commit` → auto format + lint. Lỗi format sửa rồi commit lại.

## Checklist

- [ ] `uv run pytest` local pass 100%
- [ ] Coverage ≥ 80%
- [ ] CI pipeline xanh
- [ ] Lint + type check trong CI
- [ ] Pre-commit hook cài đặt
- [ ] README có badge build + coverage
- [ ] Test chạy < 30 giây trên CI

## Bài tập cuối phase

1. Setup CI cho Blog API repo, push lên GitHub, xem badge xanh
2. Cố tình break 1 test → PR → CI phải đỏ
3. Fix test → merge → CI xanh
4. Thêm coverage threshold `--cov-fail-under=85` → điều chỉnh lại test cho đủ
