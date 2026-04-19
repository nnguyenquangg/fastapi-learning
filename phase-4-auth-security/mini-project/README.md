# Mini-project: Blog API Secure Edition

Thêm auth + RBAC + hardening vào Blog API từ Phase 3.

## Checklist implement

### 1. Auth core
- [ ] Module `app/security.py`: hash_password, verify_password, create_tokens, decode_token
- [ ] Config JWT_SECRET, JWT_ALGO, ACCESS_TTL, REFRESH_TTL đọc từ env (pydantic-settings)
- [ ] Migration thêm field `role` (str, default "user") vào bảng users

### 2. Endpoint auth
- [ ] `POST /auth/register` (201) — hash password, tạo user
- [ ] `POST /auth/login` — trả access + refresh (form-data OAuth2)
- [ ] `POST /auth/refresh` — rotate refresh token
- [ ] `POST /auth/logout` — revoke refresh (blacklist hoặc delete DB record)
- [ ] `GET /users/me` — trả user hiện tại

### 3. Refresh token lưu DB
Thay vì blacklist access token, store refresh:
```python
class RefreshToken(Base):
    id: int
    user_id: int
    token_hash: str        # lưu hash của token, không raw
    expires_at: datetime
    revoked_at: datetime | None
```
- Login: tạo refresh token, insert record
- Refresh: lookup by hash, verify not revoked & not expired, rotate
- Logout: mark revoked_at

### 4. Protect Blog endpoints
- [ ] `GET /posts` — public (ai cũng xem được)
- [ ] `GET /posts/{id}` — public
- [ ] `POST /posts` — **auth required**, author = current user
- [ ] `PATCH /posts/{id}` — auth + **owner** (hoặc admin)
- [ ] `DELETE /posts/{id}` — auth + owner (hoặc admin)
- [ ] `POST /posts/{id}/comments` — auth required
- [ ] `DELETE /comments/{id}` — auth + owner comment (hoặc owner post, hoặc admin)

### 5. Admin endpoints
- [ ] `DELETE /admin/users/{id}` — admin only (ban user, cascade xoá post/comment)
- [ ] `POST /admin/users/{id}/promote` — admin only (đổi role)
- [ ] Seed admin account qua CLI script, không qua API

### 6. Security hardening
- [ ] CORS chặt (chỉ frontend domain)
- [ ] Security headers middleware
- [ ] Rate limit login: 5 fail / 15 phút / IP → 429
- [ ] Rate limit global: 60 req / phút / IP
- [ ] Body size limit (cấu hình uvicorn)
- [ ] Error handler không leak stacktrace trong prod

### 7. Environment
- [ ] `.env.example` commit (không chứa secret thật)
- [ ] `.env` trong `.gitignore`
- [ ] README hướng dẫn copy `.env.example` → `.env`
- [ ] `JWT_SECRET` phải tối thiểu 32 bytes random

## File structure gợi ý

```
app/
  config.py                   # Settings
  db.py
  security.py                 # hash, jwt
  auth/
    __init__.py
    dependencies.py           # get_current_user, require_role, get_optional_user
    routes.py                 # /auth/*
    schemas.py                # LoginRequest, TokenResponse, ...
    service.py                # AuthService: register, login, refresh, logout
  models/
    user.py                   # thêm role, relationship refresh_tokens
    refresh_token.py          # new
    ...
  routers/
    posts.py                  # thêm Depends(get_current_user), ownership check
    comments.py
    admin.py                  # new
  middleware/
    rate_limit.py
    security_headers.py
  main.py
```

## Testing tự kiểm tra

Dùng Swagger UI để chạy các scenario sau:

### Happy path
1. Register user A → 201
2. Login user A → có access + refresh
3. GET /users/me với token → thấy thông tin A
4. POST /posts (auth) → 201, author_id = A
5. PATCH /posts/{id} (auth A) → 200
6. Refresh token → có access mới

### Security scenarios
1. PATCH /posts/{id} **không token** → 401
2. PATCH /posts của user B bằng token A → 403
3. DELETE /admin/users/1 bằng token user thường → 403
4. Login sai password 6 lần → 429
5. Gửi JWT bị sửa payload → 401
6. Gửi refresh token hết hạn → 401
7. Dùng access token thay refresh ở /auth/refresh → 401
8. Logout → refresh token đó dùng lại → 401

### Test tự động (bonus)
- [ ] pytest fixture tạo user + tạo token
- [ ] Test owner chỉ edit được post của mình
- [ ] Test refresh rotate
- [ ] Test rate limit

## Triển khai production-ready

- [ ] `uvicorn --workers N --proxy-headers` sau nginx
- [ ] HTTPS only (Let's Encrypt)
- [ ] Secret từ secret manager (not .env)
- [ ] Log auth event ra stdout (JSON)
- [ ] Monitor 4xx/5xx rate (Grafana, Sentry)

Xong → [Phase 5: Testing](../../phase-5-testing/PHASE.md)
