"""
Example 03 — Login flow + Auth Dependency

Gộp:
- POST /auth/register
- POST /auth/login (OAuth2PasswordRequestForm)
- GET /users/me (dùng get_current_user)

Chạy: uv run fastapi dev examples/03_login_and_auth.py
"""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

# Import từ ví dụ trước (trong project thực là app.security)
from .password import hash_password, verify_password         # noqa
from .jwt_utils import create_access_token, create_refresh_token, decode_token, InvalidTokenError  # noqa


# ============================================================
# Schemas
# ============================================================
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str = "user"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ============================================================
# Fake DB (thay bằng SQLAlchemy ở project thực)
# ============================================================
class UserRecord(BaseModel):
    id: int
    email: str
    name: str
    hashed_password: str
    role: str = "user"


FAKE_USERS: dict[str, UserRecord] = {}
_NEXT_ID = 1


def _save_user(email: str, name: str, hashed_password: str) -> UserRecord:
    global _NEXT_ID
    user = UserRecord(
        id=_NEXT_ID, email=email, name=name, hashed_password=hashed_password
    )
    FAKE_USERS[email] = user
    _NEXT_ID += 1
    return user


def _find_by_email(email: str) -> UserRecord | None:
    return FAKE_USERS.get(email)


def _find_by_id(user_id: int) -> UserRecord | None:
    return next((u for u in FAKE_USERS.values() if u.id == user_id), None)


# ============================================================
# OAuth2 scheme - báo FastAPI: đây là bearer token endpoint
# ============================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# tokenUrl = endpoint mà Swagger UI sẽ gọi khi bấm "Authorize"


# ============================================================
# Dependency: lấy current user từ token
# ============================================================
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserRecord:
    try:
        payload = decode_token(token, expected_type="access")
    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION

    user_id = int(payload["sub"])
    user = _find_by_id(user_id)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


CurrentUserDep = Annotated[UserRecord, Depends(get_current_user)]


async def require_admin(user: CurrentUserDep) -> UserRecord:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


AdminDep = Annotated[UserRecord, Depends(require_admin)]


# ============================================================
# Auth router
# ============================================================
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate) -> UserRecord:
    if _find_by_email(payload.email):
        # Generic message - không tiết lộ email đã tồn tại
        # Nhưng với register, hợp lý để báo rõ
        raise HTTPException(status_code=409, detail="Email đã được đăng ký")
    user = _save_user(
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
    )
    return user


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    """
    OAuth2PasswordRequestForm: nhận form-data (username, password)
    - username = email (mình chọn vậy)
    - password = raw password

    ⚠ Luôn trả MESSAGE GIỐNG NHAU cho "email không tồn tại" và "password sai"
    → Tránh enumerate email.
    """
    user = _find_by_email(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(
        subject=user.id,
        extra={"role": user.role},
    )
    refresh = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access, refresh_token=refresh)


class RefreshRequest(BaseModel):
    refresh_token: str


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest) -> TokenResponse:
    """
    Đổi access token mới từ refresh token.
    Project production: lưu refresh token trong DB, revoke được.
    """
    try:
        data = decode_token(payload.refresh_token, expected_type="refresh")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(data["sub"])
    user = _find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    new_access = create_access_token(subject=user_id, extra={"role": user.role})
    # Có thể rotate refresh token luôn (best practice):
    new_refresh = create_refresh_token(subject=user_id)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


# ============================================================
# Protected endpoints demo
# ============================================================
users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me", response_model=UserRead)
async def me(current: CurrentUserDep) -> UserRecord:
    return current


@users_router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, _: AdminDep) -> None:
    """Chỉ admin mới xoá được user khác."""
    user = _find_by_id(user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    FAKE_USERS.pop(user.email, None)


# ============================================================
# App
# ============================================================
app = FastAPI(title="Auth Demo")
app.include_router(auth_router)
app.include_router(users_router)


# === Test thử bằng Swagger ===
#
# 1. POST /auth/register với { "email": "a@x.com", "name": "An", "password": "password123" }
# 2. POST /auth/login: điền username=a@x.com, password=password123 → copy access_token
# 3. Bấm nút "Authorize" ở góc trên /docs, paste access_token
# 4. GET /users/me → thấy user info
# 5. Thử gọi /users/{id} DELETE → 403 (không phải admin)
#
# Tạo admin: sửa tay FAKE_USERS[email].role = "admin"
# (Project thật: seed admin từ script riêng, không qua API)


# ============================================================
# Bài tập
# ============================================================
#
# 1. Endpoint POST /auth/logout:
#    - Nhận refresh_token
#    - Revoke (thêm vào blacklist in-memory)
#    - Decode + kiểm blacklist trong decode_token
#
# 2. Endpoint POST /auth/change-password:
#    - Body: old_password, new_password
#    - Verify old, hash new
#    - Bonus: revoke tất cả refresh token của user sau đổi password
#
# 3. Rate limit login endpoint:
#    - In-memory dict {ip: [timestamps]}
#    - Quá 5 lần fail trong 1 phút → 429 Too Many Requests
#    - Không đếm login thành công
#
# 4. Refactor: tách module
#    - app/security.py (password + jwt)
#    - app/auth/dependencies.py (get_current_user, require_admin)
#    - app/auth/routes.py (endpoints)
#    - app/auth/schemas.py
