"""
Example 01 — Password Hashing với bcrypt

Install: uv add "passlib[bcrypt]"
"""
from passlib.context import CryptContext


# ============================================================
# bcrypt context
# ============================================================
# schemes: thuật toán dùng (có thể list nhiều để migrate cũ → mới)
# deprecated="auto": hash cũ (sha256 chẳng hạn) sẽ auto needs_update=True
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,   # work factor: 10 nhanh, 12 chuẩn, 14 chậm
)


def hash_password(raw: str) -> str:
    """Hash 1 password. Luôn ra hash khác nhau (có salt riêng)."""
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """So sánh raw với hash."""
    return pwd_context.verify(raw, hashed)


def needs_rehash(hashed: str) -> bool:
    """Hash có cần update không (vd đổi từ schema cũ, hoặc đổi rounds)."""
    return pwd_context.needs_update(hashed)


# ============================================================
# Demo
# ============================================================
if __name__ == "__main__":
    raw = "my-secret-password"

    hashed1 = hash_password(raw)
    hashed2 = hash_password(raw)

    print(f"Hash 1: {hashed1}")
    print(f"Hash 2: {hashed2}")
    print(f"Khác nhau? {hashed1 != hashed2}")   # True — do salt khác nhau

    print(f"Verify đúng? {verify_password(raw, hashed1)}")       # True
    print(f"Verify sai?  {verify_password('wrong', hashed1)}")   # False


# ============================================================
# Tích hợp vào flow register
# ============================================================
# @app.post("/auth/register", response_model=UserRead, status_code=201)
# async def register(payload: UserCreate, db: DbDep):
#     existing = await user_repo.get_by_email(db, payload.email)
#     if existing:
#         raise HTTPException(409, "Email đã tồn tại")
#
#     user = User(
#         email=payload.email,
#         name=payload.name,
#         hashed_password=hash_password(payload.password),   # ← hash ở đây
#     )
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return user


# ============================================================
# Lưu ý
# ============================================================
#
# 1. bcrypt giới hạn 72 bytes input → nếu password dài hơn sẽ bị cắt
#    → nhiều thư viện auto pre-hash bằng sha256 trước khi bcrypt (passlib làm rồi)
#
# 2. Work factor (rounds) = 12 tốn ~200-300ms trên laptop hiện đại
#    - Thấp quá → dễ brute force
#    - Cao quá → login chậm, DoS
#    - Benchmark trên server của bạn, chọn sao mất ~200-400ms
#
# 3. KHÔNG cần lưu salt riêng → bcrypt lưu salt trong hash string
#    Format: $2b$12$<salt><hash>
#
# 4. KHÔNG nên dùng:
#    - MD5, SHA1, SHA256 thuần — không slow function, brute force được
#    - PBKDF2 (OK nhưng weak hơn)
#
# 5. Nếu chọn argon2 (khuyến khích cho project mới):
#    from argon2 import PasswordHasher
#    ph = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=4)
#    hashed = ph.hash("password")
#    ph.verify(hashed, "password")


# ============================================================
# Bài tập
# ============================================================
#
# 1. Benchmark:
#    import time
#    - Hash 100 lần với rounds=10, 12, 14. Đo thời gian trung bình.
#    - Chọn rounds sao mỗi hash mất 200-300ms trên máy bạn
#
# 2. Viết test:
#    - hash 1 password
#    - verify đúng password → True
#    - verify sai password → False
#    - verify với hash bị corrupt → False, không crash
#
# 3. Mô phỏng migration:
#    - Giả sử trước đây bạn dùng sha256 thuần (không an toàn)
#    - Tạo CryptContext với schemes=["bcrypt", "sha256_crypt"]
#    - Verify 1 user có hash sha256 → OK, pwd_context.needs_update → True
#    - → logic: khi user login thành công, rehash bằng bcrypt
