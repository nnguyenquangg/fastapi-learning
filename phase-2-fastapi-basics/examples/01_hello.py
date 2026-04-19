"""
Example 01 — Hello FastAPI

Chạy:
    uv run fastapi dev examples/01_hello.py

Mở:
    http://127.0.0.1:8000        → JSON response
    http://127.0.0.1:8000/docs   → Swagger UI (thần thánh)
    http://127.0.0.1:8000/redoc  → ReDoc
"""
from fastapi import FastAPI

app = FastAPI(
    title="Hello FastAPI",
    description="App đầu tiên của bạn với FastAPI",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# --- Bài tập ---
# 1. Thêm endpoint GET /about trả về dict có name, version, author
# 2. Thêm endpoint GET /time trả về current time (datetime.now().isoformat())
# 3. Vào /docs, thử "Execute" từng endpoint, xem response


# --- Ghi chú ---
#
# 1. FastAPI = ASGI framework (async), chạy bằng uvicorn
# 2. `fastapi dev` = wrapper quanh uvicorn, có auto-reload
# 3. `async def` vs `def`:
#    - I/O (DB, HTTP call) → async
#    - Compute nhẹ → def cũng OK
#    - Không dùng time.sleep() trong async — dùng asyncio.sleep
# 4. Type hint của return giúp FastAPI sinh OpenAPI response schema
