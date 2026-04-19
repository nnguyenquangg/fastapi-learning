"""
Example 04 — RBAC (Role-Based Access Control) + Ownership check

Pattern phổ biến:
- Role: user, editor, admin
- Ownership: user chỉ được edit/xoá resource của chính mình
- Admin: bypass ownership (xem/xoá mọi thứ)

2 cách check:
1. Dependency → đảm bảo role trước khi vào endpoint
2. Trong endpoint/service → check ownership khi có data
"""
from enum import Enum
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel


# ============================================================
# Roles & Permissions
# ============================================================
class Role(str, Enum):
    USER = "user"
    EDITOR = "editor"
    ADMIN = "admin"


class User(BaseModel):
    id: int
    email: str
    role: Role


# ============================================================
# Dependency factory: require role
# ============================================================
def require_role(*allowed: Role):
    """
    Factory tạo dependency check role.
    Dùng:
        @app.get(..., dependencies=[Depends(require_role(Role.ADMIN))])
    Hoặc inject vào handler:
        async def handler(_: Annotated[User, Depends(require_role(Role.ADMIN))]): ...
    """
    async def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in allowed]}",
            )
        return user
    return dependency


# ============================================================
# Permission-based (flexible hơn)
# ============================================================
class Permission(str, Enum):
    READ_ANY_POST = "read:any_post"
    EDIT_ANY_POST = "edit:any_post"
    DELETE_ANY_POST = "delete:any_post"
    BAN_USER = "ban:user"


# Map role → permissions (nên đọc từ DB trong prod)
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.USER: set(),
    Role.EDITOR: {Permission.READ_ANY_POST, Permission.EDIT_ANY_POST},
    Role.ADMIN: set(Permission),   # all
}


def has_permission(user: User, perm: Permission) -> bool:
    return perm in ROLE_PERMISSIONS.get(user.role, set())


def require_permission(*perms: Permission):
    async def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not all(has_permission(user, p) for p in perms):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return dependency


# ============================================================
# Ownership check (dùng trong service, không phải dependency)
# ============================================================
class Post(BaseModel):
    id: int
    title: str
    author_id: int
    content: str


FAKE_POSTS: dict[int, Post] = {
    1: Post(id=1, title="Post 1", author_id=1, content="..."),
    2: Post(id=2, title="Post 2", author_id=2, content="..."),
}


def ensure_can_edit_post(post: Post, user: User) -> None:
    """
    Owner (author) HOẶC ai có permission EDIT_ANY_POST đều được.
    """
    if post.author_id == user.id:
        return
    if has_permission(user, Permission.EDIT_ANY_POST):
        return
    raise HTTPException(status_code=403, detail="Not the owner")


def ensure_can_delete_post(post: Post, user: User) -> None:
    if post.author_id == user.id:
        return
    if has_permission(user, Permission.DELETE_ANY_POST):
        return
    raise HTTPException(status_code=403, detail="Cannot delete this post")


# ============================================================
# Fake current user (thay bằng JWT decode thực)
# ============================================================
async def get_current_user() -> User:
    """Placeholder: trong thực tế decode JWT như ví dụ 03."""
    return User(id=1, email="a@x.com", role=Role.USER)


# ============================================================
# Demo routes
# ============================================================
app = FastAPI()


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminOnly = Annotated[User, Depends(require_role(Role.ADMIN))]
EditorOrAdmin = Annotated[User, Depends(require_role(Role.EDITOR, Role.ADMIN))]


@app.get("/posts/{post_id}")
async def get_post(post_id: int, _: CurrentUser) -> Post:
    post = FAKE_POSTS.get(post_id)
    if post is None:
        raise HTTPException(404, "Not found")
    return post


@app.put("/posts/{post_id}")
async def update_post(post_id: int, user: CurrentUser) -> dict:
    post = FAKE_POSTS.get(post_id)
    if post is None:
        raise HTTPException(404, "Not found")
    ensure_can_edit_post(post, user)   # ← ownership check
    # ... update logic
    return {"ok": True}


@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: int, user: CurrentUser) -> None:
    post = FAKE_POSTS.get(post_id)
    if post is None:
        raise HTTPException(404)
    ensure_can_delete_post(post, user)
    del FAKE_POSTS[post_id]


@app.delete("/admin/users/{user_id}", status_code=204)
async def ban_user(user_id: int, _: AdminOnly) -> None:
    """Endpoint admin only - route-level check."""
    ...


@app.get("/admin/reports")
async def reports(
    _: Annotated[User, Depends(require_permission(Permission.READ_ANY_POST))],
) -> list[dict]:
    """Endpoint dựa trên permission, không phải role."""
    return [{"count": len(FAKE_POSTS)}]


# ============================================================
# Pattern quan trọng: expose permission trong response
# ============================================================
class PostWithPerms(BaseModel):
    id: int
    title: str
    content: str
    can_edit: bool      # frontend dùng để enable/disable button
    can_delete: bool


@app.get("/posts/{post_id}/detail", response_model=PostWithPerms)
async def get_post_detail(post_id: int, user: CurrentUser) -> dict:
    post = FAKE_POSTS.get(post_id)
    if post is None:
        raise HTTPException(404)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "can_edit": post.author_id == user.id or has_permission(user, Permission.EDIT_ANY_POST),
        "can_delete": post.author_id == user.id or has_permission(user, Permission.DELETE_ANY_POST),
    }


# ============================================================
# Bài tập
# ============================================================
#
# 1. Thêm role MODERATOR có quyền EDIT_ANY_POST nhưng không DELETE_ANY_POST.
#    Test: user có role này chỉ edit được, không delete được
#
# 2. Resource-level role (owner, editor, viewer của từng post):
#    - Bảng post_permissions(post_id, user_id, level)
#    - ensure_can_edit_post: check thêm từ bảng này
#    - Pattern này phù hợp app kiểu Google Docs (share riêng mỗi doc)
#
# 3. Dependency `get_current_user_optional` trả về User | None:
#    - Có token → decode
#    - Không token → None
#    - Dùng cho endpoint public (list post) nhưng cần biết user để show can_edit
#
# 4. Logging audit:
#    - Log mỗi lần admin thực hiện action (who, what, when, target)
#    - Lưu vào bảng audit_log
