# Phase 5 — Testing

**Thời gian:** 5-7 ngày
**Mục tiêu:** Test FastAPI app đủ tự tin refactor/deploy không sợ vỡ.

## Triết lý test

```
         ▲
        E2E          (ít, chậm, đắt - 5%)
       ─────
      Integration     (vừa đủ, vừa nhanh - 20%)
     ─────────────
    Unit tests          (nhiều, nhanh - 75%)
   ─────────────────
```

**Chiến lược cho backend FastAPI:**
- **Unit** cho business logic thuần (service, helper)
- **Integration** test endpoint với real DB (Postgres test riêng) — ROI cao nhất
- **E2E** rất ít, chỉ cho critical flow (signup → login → tạo post → xoá)

## Bạn sẽ học được gì

- pytest cơ bản + advanced (fixture, parametrize, markers)
- pytest-asyncio cho async test
- httpx AsyncClient để test FastAPI
- Test DB isolation: transaction rollback / truncate
- Mock với `unittest.mock` + `pytest-mock`
- Test coverage
- CI/CD integration (GitHub Actions)

## Kế hoạch

| Ngày | Chủ đề | File |
|------|--------|------|
| 1 | pytest cơ bản, fixture | `examples/01_pytest_basics.py` |
| 2 | Test async function | `examples/02_async_tests.py` |
| 3 | Test FastAPI endpoint (unit, không DB) | `examples/03_test_endpoints.py` |
| 4 | Test với DB thật (integration) | `examples/04_test_with_db.py` |
| 5 | Test auth flow | `examples/05_test_auth.py` |
| 6 | Mock & factory | `examples/06_mock_factory.py` |
| 7 | CI + coverage | `ci-and-coverage.md` |

## Setup

```bash
uv add --dev pytest pytest-asyncio pytest-cov httpx pytest-mock factory-boy
```

`pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"       # tự động detect async test, không cần @pytest.mark.asyncio
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-ra --strict-markers"
markers = [
    "slow: tests chạy chậm",
    "integration: cần DB thật",
]

[tool.coverage.run]
branch = true
source = ["app"]
omit = ["app/migrations/*", "tests/*"]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 80
```

## Quy tắc viết test tốt

### ✅ DO
- **1 test = 1 hành vi** (không test 10 thứ trong 1 test)
- **Tên test mô tả behavior**: `test_login_with_wrong_password_returns_401`
- **AAA pattern**: Arrange → Act → Assert
- **Data độc lập**: mỗi test tự seed data của mình, không phụ thuộc test khác
- **Fail message rõ ràng**: dùng `assert x == y`, pytest tự show diff
- **Test behavior, không implementation**: test "POST /users tạo user" không test "gọi repo.create(...)"

### ❌ DON'T
- ❌ Test chia sẻ state (global dict, class-level var)
- ❌ Sleep trong test - dùng mock time hoặc fixture
- ❌ Hit external API thật trong test - mock
- ❌ Test dài, phức tạp - tách nhỏ
- ❌ Dùng `try/except` thay `pytest.raises` - assertion explicit hơn
- ❌ Skip test "tạm thời" mà không ticket

## Test pyramid cho Blog API

### Unit (thuần logic, không DB, không I/O)
- `security.hash_password` / `verify_password`
- `jwt_utils.create_access_token` / `decode_token`
- `slug_from_title`
- Pydantic validators (edge cases)

### Integration (endpoint + real DB)
- POST /auth/register → user được insert
- POST /auth/login đúng/sai password → 200/401
- CRUD post đầy đủ happy + error path
- Ownership: user A không edit được post user B
- Pagination chính xác

### E2E
- Full flow: register → login → create post → add comment → logout

## Test DB strategy

### Option 1: Truncate tables sau mỗi test (đơn giản)
```python
@pytest.fixture(autouse=True)
async def clean_db(db: AsyncSession):
    yield
    for table in reversed(Base.metadata.sorted_tables):
        await db.execute(table.delete())
    await db.commit()
```

### Option 2: Transaction rollback (nhanh hơn, phổ biến)
```python
@pytest.fixture
async def db():
    async with engine.connect() as conn:
        trans = await conn.begin()
        async_session = AsyncSession(conn, expire_on_commit=False)
        yield async_session
        await async_session.close()
        await trans.rollback()
```

**⚠** Option 2 cần thêm nested transaction / savepoint nếu code app gọi `commit()` — SQLAlchemy có sẵn support.

## Mini-project

Viết test cho **Blog API** đã làm ở Phase 3/4:
- Coverage ≥ 80%
- Cover đủ auth flow
- Cover ownership check
- Chạy trong < 10 giây
- Chạy được trên CI (GitHub Actions)

Xem [mini-project/README.md](mini-project/README.md).

## Checklist

- [ ] `uv run pytest` chạy ra kết quả
- [ ] Coverage ≥ 80%
- [ ] Test DB riêng, reset sau mỗi test
- [ ] Có auth fixture (tạo user + token sẵn)
- [ ] Test cả happy path + error path
- [ ] CI pipeline chạy test trên push
- [ ] Không có test flaky (chạy 10 lần đều pass)

→ [Phase 6: Production Project](../phase-6-production-project/PHASE.md)
