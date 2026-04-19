"""
Example 05 — Security Hardening

Checklist OWASP căn bản + rate limit + security headers.
"""
import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


app = FastAPI()


# ============================================================
# 1. CORS đúng cách
# ============================================================
app.add_middleware(
    CORSMiddleware,
    # ⚠ KHÔNG dùng ["*"] nếu có allow_credentials=True
    allow_origins=[
        "https://yourdomain.com",
        "http://localhost:5173",   # dev frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)


# ============================================================
# 2. Trusted Host (tránh Host header injection)
# ============================================================
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "api.yourdomain.com", "localhost", "127.0.0.1"],
)


# ============================================================
# 3. Security headers (helmet-style)
# ============================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # HSTS chỉ enable khi chắc chắn dùng HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        # CSP tùy app:
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# ============================================================
# 4. Rate Limit đơn giản (in-memory, per IP)
# ============================================================
# ⚠ In-memory = reset khi restart, không share giữa worker
# Production: Redis + slowapi/aiolimiter

class InMemoryRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 60, period_seconds: int = 60) -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Chỉ áp cho auth endpoint (ví dụ)
        if not request.url.path.startswith("/auth"):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.time()
        hits = self._hits[ip]
        # Dọn dấu cũ hơn period
        while hits and now - hits[0] > self.period:
            hits.popleft()
        if len(hits) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Too many requests"},
                headers={"Retry-After": str(self.period)},
            )
        hits.append(now)
        return await call_next(request)


app.add_middleware(InMemoryRateLimiter, calls=10, period_seconds=60)


# ============================================================
# 5. Login throttle (chỉ đếm fail)
# ============================================================
_login_fails: dict[str, deque[float]] = defaultdict(deque)
LOGIN_MAX_FAILS = 5
LOGIN_WINDOW = 60 * 15   # 15 phút


def check_login_throttle(ip: str) -> None:
    now = time.time()
    fails = _login_fails[ip]
    while fails and now - fails[0] > LOGIN_WINDOW:
        fails.popleft()
    if len(fails) >= LOGIN_MAX_FAILS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts, try again later",
            headers={"Retry-After": str(LOGIN_WINDOW)},
        )


def record_login_fail(ip: str) -> None:
    _login_fails[ip].append(time.time())


def reset_login_fails(ip: str) -> None:
    _login_fails[ip].clear()


# Dùng trong login endpoint:
# @app.post("/auth/login")
# async def login(request: Request, form: ...):
#     ip = request.client.host
#     check_login_throttle(ip)
#     user = ... verify ...
#     if not user:
#         record_login_fail(ip)
#         raise HTTPException(401, "Invalid credentials")
#     reset_login_fails(ip)
#     return ...


# ============================================================
# 6. Body size limit (chống upload DoS)
# ============================================================
# Uvicorn/Hypercorn: cấu hình ở server level
# uvicorn --limit-max-request-size 1048576   # 1MB
# Hoặc nginx/envoy phía trước: client_max_body_size


# ============================================================
# 7. Input sanitization
# ============================================================
# Pydantic đã validate type + constraint → đủ trong 90% case
# Nhưng với field tự do (text, markdown), cẩn thận:
# - XSS: escape khi render (frontend lo, nhưng API nên reject HTML tags nếu không cần)
# - SQL injection: KHÔNG dùng f-string với SQL, dùng parameterized (SQLAlchemy đã làm)
# - Path traversal: không nhận tên file kèm '..', '/'

from pydantic import BaseModel, Field, field_validator


class SafeTextInput(BaseModel):
    content: str = Field(max_length=10_000)

    @field_validator("content")
    @classmethod
    def strip_control_chars(cls, v: str) -> str:
        # Loại control char không in được (trừ \n, \t)
        return "".join(c for c in v if c.isprintable() or c in "\n\t")


# ============================================================
# 8. Không leak info trong error
# ============================================================
@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Production: KHÔNG trả stacktrace ra client."""
    # Log đầy đủ về server
    import logging
    logging.exception("Unhandled: %s %s", request.method, request.url.path)
    # Trả generic
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ============================================================
# 9. Secrets management
# ============================================================
# ❌ KHÔNG commit .env
# ✅ .env.example (không chứa secret thật) commit vào repo
# ✅ .env trong .gitignore
# ✅ Production: dùng secret manager (AWS Secrets Manager, GCP Secret Manager, Doppler, Vault)

# pyproject.toml / .env.example:
# DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST/DB
# JWT_SECRET=replace-with-random-32-bytes
# ENVIRONMENT=development


# ============================================================
# OWASP Top 10 — Mini Checklist
# ============================================================
# A01 Broken Access Control       → RBAC + ownership check (ví dụ 04)
# A02 Cryptographic Failures      → bcrypt password, TLS, secret từ env
# A03 Injection                   → SQLAlchemy parameterized, Pydantic validate
# A04 Insecure Design             → threat modeling, review auth flow
# A05 Security Misconfiguration   → CORS chặt, security headers, tắt debug mode prod
# A06 Vulnerable Components       → uv lock, renovate/dependabot
# A07 Auth & Identification       → lockout, MFA, strong password, session mgmt
# A08 Software Integrity          → verify npm/pypi hashes (uv lock), sign releases
# A09 Logging & Monitoring        → log auth event, detect anomaly
# A10 SSRF                        → validate URL, deny private IP ranges


# ============================================================
# Bài tập
# ============================================================
#
# 1. Thay in-memory rate limiter bằng Redis (nếu có sẵn)
#    - Dùng slowapi hoặc tự viết với redis.asyncio
#
# 2. Endpoint POST /uploads:
#    - Chỉ nhận file .png/.jpg
#    - Giới hạn 5MB
#    - Sanitize filename (không dùng filename user gửi làm path)
#    - Lưu ra UUID, mapping metadata vào DB
#
# 3. Viết test:
#    - Gọi /auth/login 6 lần fail → lần 6 bị 429
#    - Đợi 15 phút (test có thể mock time) → gọi lại được
#
# 4. Threat model cho Blog API:
#    - Ai là attacker? (user tò mò, spammer, automated bot)
#    - Họ cố gắng đạt gì?
#    - Endpoint nào là "honeypot" cho attack?
#    - Viết 5-10 dòng ra mô tả
