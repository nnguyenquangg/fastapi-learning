# Setup Môi Trường

Làm một lần, dùng cho cả roadmap.

## 1. Cài Python 3.11+

### macOS
```bash
brew install python@3.12
python3.12 --version   # kiểm tra
```

### Kiểm tra
```bash
python3 --version   # phải >= 3.11
```

> **Tại sao 3.11+?** FastAPI hiện đại dùng syntax `X | None` (PEP 604), `Annotated`, và performance improvements của Python 3.11.

## 2. Cài `uv` - package manager hiện đại

`uv` nhanh hơn pip ~10-100 lần, quản lý virtualenv gọn hơn. Hoặc có thể dùng `pip`/`poetry` nếu quen.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

## 3. Cài PostgreSQL

### Option A: Docker (recommended - sạch, dễ xoá)
```bash
docker run --name learn-pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=learning \
  -p 5432:5432 \
  -d postgres:16
```

Kiểm tra:
```bash
docker exec -it learn-pg psql -U postgres -d learning -c "SELECT version();"
```

### Option B: Native (macOS)
```bash
brew install postgresql@16
brew services start postgresql@16
createdb learning
```

## 4. Cài GUI client (tùy chọn, nhưng nên có)

- **TablePlus** (macOS, free tier) - nhẹ
- **DBeaver** (cross-platform, free) - full feature
- **pgAdmin** - official

## 5. Editor

**VSCode** + các extension:
- Python (Microsoft)
- Pylance
- Ruff (linter/formatter)
- SQLTools + SQLTools PostgreSQL Driver

Settings đề xuất (`.vscode/settings.json`):
```json
{
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  }
}
```

## 6. Git

```bash
git --version   # nếu chưa có thì brew install git
cd /Users/mac/Desktop/Wang-spaces/fastapi-learning
git init
git add .
git commit -m "chore: init fastapi learning roadmap"
```

## 7. Verification checklist

Chạy các lệnh sau, tất cả phải pass:

```bash
python3 --version          # >= 3.11
uv --version               # any
docker ps                  # thấy learn-pg đang chạy (nếu chọn option A)
psql --version             # hoặc dùng docker exec
git --version              # >= 2.0
code --version             # nếu dùng VSCode
```

Xong 7 bước này → sang [Phase 0](phase-0-python-basics/PHASE.md).
