# Common Pitfalls — Những cái bẫy thường gặp

Tập hợp lỗi lặp đi lặp lại mà newbie (và không-so-newbie) hay mắc.

## 1. Trộn sync và async

```python
# ❌ Block event loop
@app.get("/stuff")
async def handler():
    time.sleep(5)                   # ❌ BLOCK
    response = requests.get("...")  # ❌ BLOCK
    return response.json()
```

```python
# ✅ Async toàn bộ
@app.get("/stuff")
async def handler():
    await asyncio.sleep(5)
    async with httpx.AsyncClient() as client:
        response = await client.get("...")
    return response.json()
```

**Quy tắc:** trong `async def`, không gọi function sync làm I/O. Nếu bắt buộc (thư viện cũ): `await asyncio.to_thread(sync_fn, ...)`.

## 2. Quên await

```python
# ❌
result = fetch_user(1)      # trả về Coroutine object
# if result: ...            # luôn True vì object không phải None

# ✅
result = await fetch_user(1)
```

Nếu thấy `<coroutine object ... at 0x...>` trong log → quên `await`.

## 3. Return ORM object thiếu response_model

```python
# ❌ — tất cả field ORM leak ra, kể cả hashed_password, internal notes
@app.get("/users/{id}")
async def get_user(id: int, db: DbDep) -> User:
    return await db.get(User, id)
```

```python
# ✅
@app.get("/users/{id}", response_model=UserRead)
async def get_user(id: int, db: DbDep):
    return await db.get(User, id)
```

`response_model=UserRead` filter ra đúng field muốn expose.

## 4. Pydantic V1 syntax trong project V2

```python
# ❌ V1
class User(BaseModel):
    email: str

    class Config:
        orm_mode = True

    @validator("email")
    def check(cls, v):
        ...
```

```python
# ✅ V2
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str

    @field_validator("email")
    @classmethod
    def check(cls, v: str) -> str:
        ...
```

## 5. N+1 query với async ORM

```python
# ❌ Lỗi MissingGreenlet hoặc nhiều query
posts = (await db.scalars(select(Post))).all()
for p in posts:
    print(p.author.name)      # lazy load fail
```

```python
# ✅ Eager load
posts = (await db.scalars(
    select(Post).options(selectinload(Post.author))
)).all()
for p in posts:
    print(p.author.name)      # đã load sẵn
```

## 6. Commit nhiều lần trong 1 request

```python
# ❌ Mỗi item 1 transaction
async def bulk_process(items):
    for item in items:
        item.status = "done"
        await db.commit()   # ❌
```

```python
# ✅ 1 transaction cho cả batch
async def bulk_process(items):
    for item in items:
        item.status = "done"
    await db.commit()
```

Commit = flush + chốt transaction. Nhiều commit = nhiều transaction = chậm + mất ACID.

## 7. `allow_origins=["*"]` + `allow_credentials=True`

Spec HTTP cấm combo này. Browser sẽ reject. Phải chỉ định origin cụ thể:

```python
# ❌
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

# ✅
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourapp.com"],
    allow_credentials=True,
)
```

## 8. Hardcode secret

```python
# ❌
SECRET_KEY = "my-secret-123"
```

```python
# ✅
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str

settings = Settings()
```

Secret từ env → không commit → rotate dễ.

## 9. Tiết lộ "email không tồn tại" vs "password sai"

```python
# ❌ Lộ enumerate
if not user:
    raise HTTPException(404, "Email không tồn tại")
if not verify_password(...):
    raise HTTPException(401, "Password sai")
```

```python
# ✅ Generic
if not user or not verify_password(...):
    raise HTTPException(401, "Invalid credentials")
```

Attacker không biết email nào đã đăng ký → khó brute force hơn.

## 10. Log request body chứa password

```python
# ❌
@app.middleware("http")
async def log_body(request, call_next):
    body = await request.body()
    logger.info("body: %s", body)   # login request body có password!
```

→ Redact hoặc không log body của auth endpoint.

## 11. `access_token` TTL quá dài

```python
# ❌
create_access_token(..., expires_delta=timedelta(days=30))
```

Leak 1 lần = compromised 30 ngày. Chuẩn:
- access: 15-30 phút
- refresh: 7-30 ngày (lưu DB, revoke được)

## 12. Hash password sai cách

```python
# ❌
import hashlib
hashed = hashlib.sha256(password.encode()).hexdigest()
```

SHA256 thuần → brute force được. Phải dùng slow function + salt:

```python
# ✅
from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"])
hashed = pwd.hash(password)
```

## 13. Migration sai thứ tự field

```python
# ❌ Drop column có data quan trọng
def upgrade():
    op.drop_column("users", "old_email")  # mất data
```

```python
# ✅ Tách 2 release
# Release 1: ngừng ghi vào old_email, migrate data sang new column
# Release 2: drop old_email
```

## 14. Không xử lý DB connection pool

- Code hit `Pool exhausted` khi traffic tăng
- Quên close session → connection leak

```python
# ❌
session = SessionLocal()
...  # không close

# ✅
async with SessionLocal() as session:
    ...

# hoặc dùng get_db dependency
```

## 15. Test chạy đúng thứ tự, sai thứ tự khác là fail

```python
# ❌ Test 1 tạo user id=1, test 2 assume user id=1 tồn tại
def test_create():
    create_user(id=1)

def test_get():
    user = get_user(1)   # fail nếu chạy trước test_create
```

→ Fixture reset DB giữa test. Cài `pytest-randomly` để lộ dependency.

## 16. Dùng `datetime.utcnow()` tùy tiện

```python
# ❌ Timezone naive, so sánh với aware sẽ lỗi
now = datetime.utcnow()
```

```python
# ✅
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```

Trong model, luôn dùng `DateTime(timezone=True)`.

## 17. Đặt business logic trong router

```python
# ❌ Router làm việc của service
@app.post("/orders")
async def create_order(db: DbDep, payload: OrderCreate):
    # 50 dòng logic: tính tổng, check stock, tạo order, trừ stock, commit...
```

```python
# ✅ Router chỉ parse request, gọi service
@app.post("/orders")
async def create_order(db: DbDep, payload: OrderCreate, user: CurrentUserDep):
    return await OrderService(db).place(user.id, payload)
```

Test dễ hơn, reuse được, router gọn.

## 18. Exception nuốt chửng

```python
# ❌
try:
    await risky_op()
except Exception:
    pass   # ← im lặng, không log → debug nightmare
```

```python
# ✅
try:
    await risky_op()
except SpecificError as e:
    logger.exception("risky_op failed")
    raise HTTPException(500, "...") from e
```

Bắt cụ thể, luôn log, preserve stack trace với `from e`.

## 19. Dependency inject không đồng nhất

```python
# ❌ Mỗi nơi dùng kiểu khác nhau
async def a(db: AsyncSession = Depends(get_db)): ...
async def b(db = Depends(get_db)): ...
async def c(db: Annotated[AsyncSession, Depends(get_db)]): ...
```

→ Chuẩn hoá. Pattern mình khuyến khích:
```python
DbDep = Annotated[AsyncSession, Depends(get_db)]

async def a(db: DbDep): ...
async def b(db: DbDep): ...
```

## 20. Dùng `*` import

```python
# ❌
from app.models import *
```

Namespace rối, IDE không autocomplete, debug khó. Luôn import cụ thể:
```python
from app.models import User, Post, Comment
```

---

## Khi bạn thấy bug

Hỏi bản thân:
1. Mình có trong list này không?
2. Nếu không → google exact error message
3. Nếu vẫn không → minimal reproduce + post lên StackOverflow/Discord

Mọi bug đã có người gặp rồi. Google tiếng Anh.
