# Debugging Tips cho FastAPI + SQLAlchemy

## Nguyên tắc chung

### 1. Đọc traceback từ DƯỚI lên
- Dòng cuối = lỗi thực sự
- Các dòng trước = chain of calls dẫn tới đó
- Tìm dòng đầu tiên thuộc code của BẠN (không phải framework)

### 2. Isolate bug
- Sao chép lại lỗi ở môi trường nhỏ nhất có thể
- Bớt code đi cho tới khi bug biến mất → dòng vừa bớt = nguyên nhân

### 3. Print > Debugger > Log (theo thứ tự ưu tiên tình huống)
- **Print**: nhanh, disposable
- **pdb/ipdb**: khi cần step through, kiểm tra state
- **Log**: cho bug production không reproduce được local

## FastAPI specific

### 422 Unprocessable Entity
```
Body: {"detail": [{"loc": ["body", "email"], "msg": "field required", ...}]}
```
→ Check: body JSON đúng field, đúng type. Xem `/docs` để biết schema kỳ vọng.

### 404 khi path đúng
- FastAPI redirect `/users` → `/users/` (307) nếu router có trailing slash
- Check APIRouter `prefix` và `@router.get("/")` có kết hợp đúng
- Try `/users/` (có slash)

### 401 hoài, token trông đúng
```bash
# Debug JWT tại jwt.io (chú ý: token nhạy cảm, đừng paste prod token)
# Hoặc trong Python:
python -c "import jose.jwt as j; print(j.get_unverified_claims('<token>'))"
```
- Token hết hạn? Check `exp` claim
- Token sai type? (access vs refresh)
- SECRET_KEY giữa code tạo và verify có giống nhau?

### Validation không trigger
- `@field_validator` thiếu `@classmethod`?
- Model không extend `BaseModel`?
- `model_config = ConfigDict(str_strip_whitespace=True)` — lưu ý là class attribute, không phải method

### Dependency không resolve
- Thiếu `Depends()`?
- Dùng dependency async nhưng quên `await` trong code gọi trực tiếp?
- Dependency return type mismatch với `Annotated`?

## SQLAlchemy specific

### `MissingGreenlet`
```
greenlet.error: cannot switch to a different thread
```
→ Bạn đang access lazy attribute trong async context:
```python
# ❌
posts = (await db.scalars(select(Post))).all()
for p in posts:
    print(p.author.name)   # lazy load → BOOM

# ✅
posts = (await db.scalars(
    select(Post).options(selectinload(Post.author))
)).all()
```

### Duplicate rows khi joinedload
```python
stmt = select(Post).options(joinedload(Post.tags))
posts = (await db.scalars(stmt)).unique().all()   # thêm .unique()
```

### Object "expire" sau commit
```
DetachedInstanceError: Instance <User> is not bound to a Session
```
→ Set `expire_on_commit=False` trong sessionmaker:
```python
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

### Query chậm bất thường
```python
# Bật echo trong dev
engine = create_async_engine(url, echo=True)

# Xem plan trực tiếp trong Postgres:
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```
Thường là:
- Thiếu index trên FK
- N+1 loading
- `LIKE '%xxx%'` không dùng được index (dùng full-text search)

### IntegrityError khó hiểu
```
IntegrityError: (asyncpg.exceptions.UniqueViolationError)
duplicate key value violates unique constraint "users_email_key"
```
→ Check constraint name, biết column nào vi phạm. Nên xử lý:
```python
try:
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    if "users_email_key" in str(e.orig):
        raise HTTPException(409, "Email already exists") from e
    raise
```

### Pool exhausted
```
QueuePool limit of size 5 overflow 10 reached
```
→ Đang giữ session quá lâu / không đóng:
- Luôn dùng `async with` hoặc get_db dependency
- Không tạo session trong function được gọi nhiều lần
- Tăng `pool_size` chỉ khi thật cần

## Python async

### Quên `await`
```python
result = fetch_user(1)   # ← trả Coroutine, KHÔNG phải data
# print(result) → <coroutine object ...>

result = await fetch_user(1)   # ✅
```

### Sync trong async
```python
async def handler():
    time.sleep(5)       # ❌ block toàn event loop
    await asyncio.sleep(5)   # ✅
```
→ Nếu thật sự cần sync (thư viện cũ): `await asyncio.to_thread(sync_func, args)`

### `RuntimeError: event loop is already running`
- Chạy `asyncio.run()` trong Jupyter? Dùng `await` trực tiếp
- Nested asyncio.run? Refactor, gọi 1 lần ở entry point

## Pydantic V2

### `@validator` không hoạt động
→ V1 syntax. Dùng `@field_validator` và `@classmethod`:
```python
@field_validator("email")
@classmethod
def check(cls, v: str) -> str: ...
```

### `class Config` không hoạt động
→ V1 syntax. Dùng:
```python
model_config = ConfigDict(from_attributes=True, ...)
```

### `Optional[X]` warning
→ Python 3.10+ prefer `X | None`:
```python
name: str | None = None
```

## Docker / Deployment

### Container start lên rồi die ngay
```bash
docker logs <container>   # xem error
docker run -it <image> /bin/sh   # vào shell debug
```

### DB connect được local, không được trong Docker
- Host: `localhost` trong container = chính container, không phải host machine
- Trong docker-compose: dùng service name (`db` thay vì `localhost`)
- Host machine trong container: `host.docker.internal` (macOS/Windows)

### Migration không chạy khi deploy
- Add vào entrypoint: `alembic upgrade head && uvicorn ...`
- Hoặc tách job riêng chạy trước khi start app

## Logging để debug production

### Structured log
```python
import structlog
logger = structlog.get_logger()

logger.info("user.login", user_id=user.id, ip=request.client.host)
```

### Request ID tracing
```python
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response
```

### Sentry
```python
import sentry_sdk
sentry_sdk.init(dsn=settings.sentry_dsn, environment="production")
# Exception tự động được capture
```

## Câu hỏi self-check khi stuck

1. Tôi có biết error message nói gì không? (Nếu không → google exact message)
2. Tôi đã reproduce được chưa? Có stable không?
3. Lần cuối code chạy được là khi nào? `git log` / `git bisect`
4. Có ai gặp vấn đề này chưa? (GitHub issues, StackOverflow)
5. Nếu nghỉ 15 phút quay lại, tôi còn bí không?

## Tools hữu ích

| Tool | Mục đích |
|------|---------|
| `httpie` hoặc `curl` | Test API từ terminal |
| **Bruno** / Postman | GUI test API, lưu collection |
| **TablePlus** / DBeaver | Inspect DB |
| `pgcli` | CLI Postgres có autocomplete |
| `uv run ipython` | REPL có autocomplete, history |
| `rich.print` | Print object đẹp hơn `print` |
| **VSCode Python debugger** | Breakpoint, step, inspect |
| **Sentry** | Track error production |
| **Grafana / Better Stack** | Log/metric dashboard |

## Câu mantra

> "When in doubt, print it out."
> — Ai đó thông thái
