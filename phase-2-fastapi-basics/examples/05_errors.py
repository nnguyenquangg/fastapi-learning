"""
Example 05 — Error Handling, Middleware, CORS, Background Tasks

Chạy: uv run fastapi dev examples/05_errors.py
"""
import logging
import time
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

app = FastAPI()


# ============================================================
# CORS (cho frontend khác domain gọi được)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dev: frontend Vite
    # allow_origins=["*"],                     # KHÔNG dùng trong production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Custom middleware (log thời gian request)
# ============================================================
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Response-Time"] = f"{elapsed:.3f}s"
    logger.info("%s %s %s %.3fs", request.method, request.url.path, response.status_code, elapsed)
    return response


# ============================================================
# Custom exception
# ============================================================
class NotFoundError(Exception):
    def __init__(self, resource: str, identifier: str | int) -> None:
        self.resource = resource
        self.identifier = identifier


class BusinessRuleError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "resource": exc.resource, "id": exc.identifier},
    )


@app.exception_handler(BusinessRuleError)
async def business_handler(_: Request, exc: BusinessRuleError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "business_rule", "message": exc.message},
    )


# Custom handler cho validation (đổi format default 422)
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


# ============================================================
# Dùng exception trong endpoint
# ============================================================
FAKE_DB = {1: {"id": 1, "balance": 100}}


@app.get("/accounts/{account_id}")
async def get_account(account_id: int) -> dict:
    if account_id not in FAKE_DB:
        raise NotFoundError("account", account_id)
    return FAKE_DB[account_id]


class TransferRequest(BaseModel):
    from_id: int
    to_id: int
    amount: float


@app.post("/transfer")
async def transfer(req: TransferRequest) -> dict:
    if req.amount <= 0:
        raise BusinessRuleError("Amount must be positive")
    if req.from_id not in FAKE_DB:
        raise NotFoundError("account", req.from_id)
    if req.to_id not in FAKE_DB:
        raise NotFoundError("account", req.to_id)
    if FAKE_DB[req.from_id]["balance"] < req.amount:
        raise BusinessRuleError("Insufficient balance")
    FAKE_DB[req.from_id]["balance"] -= req.amount
    FAKE_DB[req.to_id]["balance"] += req.amount
    return {"status": "ok"}


# ============================================================
# HTTPException trực tiếp (shortcut cho error đơn giản)
# ============================================================
@app.get("/items/{item_id}")
async def get_item(item_id: int) -> dict:
    if item_id < 1:
        # Raise ngay, không cần custom exception
        raise HTTPException(status_code=400, detail="id phải >= 1")
    if item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id}


# ============================================================
# Background tasks (fire-and-forget, chạy sau khi response đã gửi)
# ============================================================
async def send_welcome_email(email: str) -> None:
    """Giả lập gửi email mất 2s."""
    import asyncio
    await asyncio.sleep(2)
    logger.info("✅ Sent welcome email to %s", email)


@app.post("/signup", status_code=201)
async def signup(email: str, bg: BackgroundTasks) -> dict:
    # Response trả về ngay, email gửi sau
    bg.add_task(send_welcome_email, email)
    return {"email": email, "status": "registered"}


# Khi nào dùng BackgroundTasks:
# - Task ngắn (< vài giây), không critical
# - Không cần retry, không cần persist
# - VD: log, analytics, gửi email đơn giản
#
# Khi nào cần queue thật (Celery, RQ, arq, Taskiq):
# - Task nặng, lâu
# - Cần retry khi fail
# - Cần scale horizontal


# ============================================================
# Lifespan (startup / shutdown)
# ============================================================
from contextlib import asynccontextmanager  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 App starting")
    # VD: kết nối DB pool, warm cache, load ML model
    yield
    # Shutdown
    logger.info("👋 App shutting down")
    # Close connections


# Dùng:
# app = FastAPI(lifespan=lifespan)
# Ở trên mình đã tạo app rồi nên minh hoạ ở đây. Trong project thật, khai báo
# lifespan TRƯỚC khi tạo app.


# === Bài tập ===
#
# 1. Tạo exception `PermissionDeniedError(action: str)`:
#    - handler trả 403 với {"error": "forbidden", "action": ...}
#    - endpoint POST /admin/reset-db raise exception này nếu user không phải admin
#
# 2. Viết middleware đếm request cho mỗi endpoint
#    - Lưu vào dict {path: count}
#    - Endpoint GET /stats trả về dict đó
#
# 3. Thêm background task ghi log mỗi signup vào file `signups.log`
#    (dùng aiofiles nếu muốn async file I/O, hoặc asyncio.to_thread với open())
