"""
Example 02 — JWT: Sign, Verify, Decode

Install: uv add "python-jose[cryptography]"

JWT = JSON Web Token, gồm 3 phần (header.payload.signature) cách nhau dấu chấm
- Header: algo + type
- Payload: claims (sub, exp, iat, custom...)
- Signature: HMAC/RSA dựa trên secret
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt


# ============================================================
# Config (trong project thực → Settings)
# ============================================================
SECRET_KEY = "CHANGE_ME_super_long_random_string_in_env"  # min 32 bytes
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================================
# Create token
# ============================================================
def create_access_token(
    subject: str | int,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    extra: dict[str, Any] | None = None,
) -> str:
    """
    Tạo access token.
    - subject: thường là user_id hoặc email
    - expires_delta: TTL
    - extra: claim thêm (role, permissions...)
    """
    now = datetime.now(timezone.utc)
    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }
    if extra:
        to_encode.update(extra)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str | int, expires_delta: timedelta = timedelta(days=14)) -> str:
    """Refresh token dài hạn, chỉ để đổi access token mới."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================
# Decode / Verify
# ============================================================
class InvalidTokenError(Exception):
    pass


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """
    Verify + decode token.
    Raise InvalidTokenError nếu:
    - Signature sai (bị sửa)
    - Hết hạn
    - Type khớp (access vs refresh)
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require_sub": True, "require_exp": True},
        )
    except JWTError as e:
        raise InvalidTokenError(f"Token invalid: {e}") from e

    if payload.get("type") != expected_type:
        raise InvalidTokenError(
            f"Wrong token type: expected {expected_type}, got {payload.get('type')}"
        )
    return payload


# ============================================================
# Demo
# ============================================================
if __name__ == "__main__":
    # 1. Tạo access token
    token = create_access_token(
        subject=42,
        extra={"role": "user", "email": "an@x.com"},
    )
    print(f"Token: {token[:40]}...")

    # 2. Decode
    payload = decode_token(token)
    print(f"Payload: {payload}")

    # 3. Sai signature
    broken = token[:-5] + "xxxxx"
    try:
        decode_token(broken)
    except InvalidTokenError as e:
        print(f"✅ Bắt được lỗi: {e}")

    # 4. Sai type
    refresh = create_refresh_token(subject=42)
    try:
        decode_token(refresh)   # expected access
    except InvalidTokenError as e:
        print(f"✅ Bắt được: {e}")

    # 5. Hết hạn
    short = create_access_token(42, expires_delta=timedelta(seconds=-1))
    try:
        decode_token(short)
    except InvalidTokenError as e:
        print(f"✅ Expired: {e}")


# ============================================================
# JWT pitfalls — đọc kỹ
# ============================================================
#
# 1. ❌ KHÔNG cho vào JWT:
#    - Password (kể cả hashed)
#    - Thông tin nhạy cảm (SSN, credit card)
#    → JWT chỉ signed, KHÔNG encrypted. Ai cũng đọc được payload bằng base64 decode
#
# 2. ❌ KHÔNG revoke được token đã phát
#    - Cần revoke (logout toàn cục, đổi password) → phải:
#      a. Giữ blacklist token bị revoke (Redis)
#      b. Hoặc tăng version/token_revision trên user, verify thêm
#      c. Hoặc refresh token lưu DB, delete khi logout (access vẫn valid tới exp)
#
# 3. ❌ Access token TTL dài
#    - Access: 15-30 phút là chuẩn
#    - Dài hơn = lỡ leak thì kẹt
#
# 4. ❌ Dùng `algorithms=["HS256", "none"]` hoặc không chỉ định
#    - Bị attack "alg: none" - tự forge token
#    - Luôn chỉ định `algorithms=[ALGORITHM]` (list cụ thể)
#
# 5. ❌ Secret yếu
#    - Ít nhất 32 bytes ngẫu nhiên
#    - Đọc từ env, rotate định kỳ
#    - Khi rotate: giữ cả old + new 1 thời gian → accept cả 2
#
# 6. ⚠ Header vs Cookie:
#    - Authorization: Bearer <token> - dễ implement, CSRF không lo, XSS lo
#    - Cookie httpOnly + Secure + SameSite - XSS không lấy được, cần CSRF token
#    - Chọn tùy use case. Hầu hết SPA dùng Authorization header


# ============================================================
# Bài tập
# ============================================================
#
# 1. Implement full cặp create/decode:
#    - access_token (ttl 30m)
#    - refresh_token (ttl 14d)
#    - create_password_reset_token (ttl 15m, type="reset")
#
# 2. Verify "attack":
#    - Tạo token hợp lệ
#    - Sửa payload (vd đổi sub=42 → sub=1)
#    - Decode lại — phải throw InvalidTokenError
#
# 3. Implement simple revoke list:
#    REVOKED_JTI: set[str] = set()
#    - Thêm claim `jti` (unique id) khi tạo token
#    - decode_token thêm check jti không có trong REVOKED_JTI
#    - Function revoke(jti) thêm vào set
#
# 4. Chuyển SECRET_KEY sang pydantic-settings, đọc từ env var JWT_SECRET
