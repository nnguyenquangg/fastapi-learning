# Mini-project: Test Blog API

Không tạo project mới. Phase này **viết test cho Blog API** từ Phase 3 + 4.

## Mục tiêu

- Coverage ≥ 85%
- Tất cả happy path + error path của endpoint chính được cover
- Test chạy ≤ 30 giây
- CI pipeline hoạt động

## Checklist test tối thiểu

### Unit tests
- [ ] `test_security.py`
  - hash_password: không trùng lặp, verify đúng, verify sai
  - create_access_token → decode_token round-trip
  - decode_token với token hết hạn → raise
  - decode_token với sig sai → raise
  - decode_token với type sai → raise
- [ ] `test_validators.py` (Pydantic)
  - Email xấu → 422
  - Password < 8 → 422
  - Slug có ký tự lạ → 422
  - Tag không lowercase → auto convert

### Integration: Auth
- [ ] `test_auth.py`
  - Register happy
  - Register duplicate → 409
  - Register weak password → 422
  - Login success
  - Login wrong password → 401 (cùng message với email không tồn tại)
  - Login nonexistent → 401
  - Rate limit: fail 5 lần → 429
  - Refresh success (rotate)
  - Refresh với access token → 401
  - Logout: refresh bị revoke

### Integration: Users
- [ ] `test_users.py`
  - GET /users/me (authenticated)
  - GET /users/me (no token → 401)
  - GET /users/me (invalid token → 401)
  - PATCH /users/me (update name)

### Integration: Posts
- [ ] `test_posts.py`
  - GET /posts public (chưa login)
  - GET /posts pagination
  - GET /posts?tag=python filter
  - POST /posts authenticated → 201
  - POST /posts unauthenticated → 401
  - PATCH /posts/{id} owner → 200
  - PATCH /posts/{id} not owner → 403
  - PATCH /posts/{id} admin (not owner) → 200
  - DELETE /posts/{id} owner → 204
  - DELETE /posts/{id} not owner → 403
  - POST /posts với tag: gán & lấy ra đúng

### Integration: Comments
- [ ] `test_comments.py`
  - POST comment authenticated
  - POST comment unauthenticated → 401
  - DELETE comment owner → 204
  - DELETE comment author của post → 204 (policy: owner post cũng xoá được)
  - DELETE comment người khác → 403

### Integration: Admin
- [ ] `test_admin.py`
  - DELETE /admin/users/{id} admin → 204
  - DELETE /admin/users/{id} user thường → 403
  - Promote user thành admin

## Cấu trúc test

```
tests/
├── __init__.py
├── conftest.py                  # engine, db, client, user, admin fixtures
├── helpers.py                   # create_test_user, login_and_get_token
├── factories.py                 # UserFactory, PostFactory, ...
├── test_security.py             # unit
├── test_validators.py           # unit
├── test_auth.py                 # integration
├── test_users.py
├── test_posts.py
├── test_comments.py
└── test_admin.py
```

## Tips khi viết

### Nguyên tắc 1: Tạo fixture TÁi SỬ DỤNG
Đừng copy 20 dòng setup vào mỗi test. Tách vào fixture:
```python
@pytest.fixture
async def published_post(db, test_user):
    post = Post(title="T", slug="t", content="C", author_id=test_user.id, is_published=True)
    db.add(post); await db.commit(); await db.refresh(post)
    return post
```

### Nguyên tắc 2: Đặt tên test kể chuyện
```python
# ❌ test_post_1
# ✅ test_user_cannot_edit_others_post
# ✅ test_admin_can_delete_any_post
# ✅ test_login_with_wrong_password_returns_401
```

### Nguyên tắc 3: Assert cả status và body
```python
assert response.status_code == 200
body = response.json()
assert body["email"] == "user@x.com"
assert "hashed_password" not in body   # quan trọng!
```

### Nguyên tắc 4: Dùng class để group
```python
class TestPostCreation:
    async def test_authenticated_can_create(...): ...
    async def test_unauthenticated_rejected(...): ...
    async def test_empty_title_rejected(...): ...
```

## Chạy test

```bash
# Tất cả
uv run pytest

# 1 file
uv run pytest tests/test_auth.py

# 1 test
uv run pytest tests/test_auth.py::TestLogin::test_login_success

# Verbose
uv run pytest -v

# Lần gần nhất fail
uv run pytest --lf

# Stop khi fail đầu tiên
uv run pytest -x

# Coverage
uv run pytest --cov=app --cov-report=term-missing

# Debug (pdb khi fail)
uv run pytest --pdb
```

## Checklist hoàn thành phase

- [ ] Tất cả test pass
- [ ] Coverage ≥ 85%
- [ ] Thời gian chạy ≤ 30s
- [ ] Không test nào flaky (chạy 5 lần đều pass)
- [ ] CI pipeline GitHub Actions xanh
- [ ] README có badge CI + coverage

Xong → [Phase 6: Production Project](../../phase-6-production-project/PHASE.md)
