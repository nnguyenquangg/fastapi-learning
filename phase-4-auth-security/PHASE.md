# Phase 4 — Authentication & Security

**Thời gian:** 5-7 ngày
**Mục tiêu:** Secure Blog API bằng JWT auth, role-based permission, password hashing đúng chuẩn.

## Bạn sẽ học được gì

- Password hashing (bcrypt/argon2)
- JWT: access token + refresh token
- OAuth2PasswordBearer của FastAPI
- `get_current_user` dependency
- RBAC: role/permission
- Permission check pattern
- CORS, security headers
- Rate limiting
- Input sanitization, OWASP checklist

## Tại sao tách riêng phase này?

Auth là chỗ **dễ làm sai, hậu quả nghiêm trọng** (leak account, privilege escalation).
Học sau khi đã nắm FastAPI + DB chắc → tập trung được vào security.

## Kế hoạch

| Ngày | Chủ đề | File |
|------|--------|------|
| 1 | Password hashing (bcrypt) | `examples/01_password.py` |
| 2 | JWT basic: sign, verify | `examples/02_jwt.py` |
| 3 | OAuth2 flow + login endpoint | `examples/03_login.py` |
| 4 | get_current_user + protected routes | `examples/04_auth_deps.py` |
| 5 | Refresh token | `examples/05_refresh.py` |
| 6 | RBAC + permission | `examples/06_rbac.py` |
| 7 | OWASP check, rate limit | `examples/07_hardening.py` + mini-project |

## Bối cảnh: thêm auth vào Blog API từ Phase 3

Phase này **extend** Blog API của Phase 3, không viết lại:
- Thêm field `hashed_password` (đã có từ phase 3)
- Thêm endpoint `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`
- Thêm dependency `get_current_user` cho các endpoint cần auth
- Chỉ tác giả mới được edit/xoá post của mình
- Admin có thể xoá bất kỳ post nào

## Package cần cài

```bash
uv add "passlib[bcrypt]" "python-jose[cryptography]" python-multipart
# hoặc dùng:
uv add pwdlib[argon2] pyjwt python-multipart
```

Lưu ý lựa chọn:
- **bcrypt** (passlib): phổ biến nhất, đủ dùng
- **argon2** (pwdlib): hiện đại hơn, khuyến khích với project mới
- **PyJWT** hoặc **python-jose**: đều OK. PyJWT đơn giản hơn

Ví dụ trong phase này dùng `passlib[bcrypt]` + `python-jose`.

## Nguyên tắc bất di bất dịch

### ✅ PHẢI làm
- **Hash password** bằng bcrypt/argon2 (work factor đủ cao)
- **HTTPS only** trong production (tắt http cookie Secure=True)
- **JWT secret** phải ngẫu nhiên, ít nhất 32 bytes, đọc từ env
- **Access token ngắn** (15-30 phút), refresh token dài hơn (7-30 ngày)
- **Refresh token** lưu trong DB (để revoke được)
- **Rate limit** login endpoint (chặn brute force)
- **Generic error** khi login sai: "Invalid credentials", KHÔNG nói "email không tồn tại" vs "password sai"
- **Validate input** mọi nơi (Pydantic đã giúp nhiều)

### ❌ TUYỆT ĐỐI KHÔNG
- ❌ Store password plain text, MD5, SHA256 thuần
- ❌ Hardcode secret trong code / commit vào git
- ❌ Trả hashed_password trong response (dùng response_model)
- ❌ Log request body chứa password
- ❌ `allow_origins=["*"]` với `allow_credentials=True`
- ❌ Tự roll crypto - dùng thư viện
- ❌ Self-made JWT - dùng PyJWT/python-jose
- ❌ Dùng JWT cho session ngắn thay vì cookie - cookie phù hợp hơn trong nhiều case

## Mini-project: Extend Blog API

Thêm vào Blog API của Phase 3:
- Full auth flow (register/login/refresh/logout)
- Protect CRUD post: cần login
- Owner check: chỉ owner mới update/delete post
- Role: `user` | `admin`, admin xem/xoá tất cả
- Rate limit: 5 lần login fail/phút/IP → block 15 phút
- Security headers (helmet-style)

Xem [mini-project/README.md](mini-project/README.md)

## Checklist trước Phase 5

- [ ] Register + Login + Logout hoạt động qua Swagger UI
- [ ] `/docs` có nút "Authorize" → paste token dùng được
- [ ] Owner-only CRUD enforce đúng
- [ ] Admin endpoint chỉ admin truy cập được
- [ ] Access token hết hạn → refresh thành công
- [ ] Thử attack:
  - [ ] Login 6 lần sai → bị block
  - [ ] Sửa JWT payload → server reject
  - [ ] Gọi endpoint protected không token → 401
  - [ ] Gọi endpoint admin bằng user thường → 403
  - [ ] Xoá post của user khác → 403
- [ ] Secret đọc từ env, không hardcode

→ [Phase 5: Testing](../phase-5-testing/PHASE.md)
