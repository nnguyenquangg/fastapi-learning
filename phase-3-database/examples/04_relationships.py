"""
Example 04 — Relationships & N+1 Problem

Quan trọng nhất của ORM: relationship + eager loading.
Đây là chỗ 90% bug performance xảy ra.
"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, Table, Column, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
    joinedload,
)


class Base(DeclarativeBase):
    pass


# ============================================================
# One-to-Many: User (1) ← → Post (N)
# ============================================================

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    name: Mapped[str] = mapped_column(String(100))

    # One-to-many: 1 user có nhiều post
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",   # xoá user → xoá posts
    )


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="post_tags",
        back_populates="posts",
    )


# ============================================================
# Many-to-Many: Post ↔ Tag (qua bảng trung gian post_tags)
# ============================================================

# Cách 1: Table object (không có thuộc tính mở rộng)
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags",
    )


# Cách 2: Association model (khi cần thêm field vào bảng trung gian, vd created_at)
# class PostTag(Base):
#     __tablename__ = "post_tags_v2"
#     post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
#     tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
#     added_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# ============================================================
# One-to-Many: Post ← → Comment
# ============================================================

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship()


# ============================================================
# 🚨 N+1 Problem
# ============================================================

async def bad_list_posts(db: AsyncSession) -> list[dict]:
    """
    ❌ KHÔNG làm như này trong async.
    Lazy loading trong async KHÔNG hoạt động → lỗi MissingGreenlet.
    Và kể cả nếu hoạt động → N+1: 1 query list + N query cho từng post.author
    """
    stmt = select(Post)
    posts = (await db.scalars(stmt)).all()
    result = []
    for p in posts:
        # Mỗi lần access p.author → thêm 1 query
        result.append({"title": p.title, "author": p.author.name})
    return result


async def good_list_posts_selectin(db: AsyncSession) -> list[dict]:
    """
    ✅ selectinload: 2 query tổng cộng
    - Query 1: SELECT * FROM posts
    - Query 2: SELECT * FROM users WHERE id IN (...)
    → nối lại ở Python
    """
    stmt = select(Post).options(selectinload(Post.author))
    posts = (await db.scalars(stmt)).all()
    return [{"title": p.title, "author": p.author.name} for p in posts]


async def good_list_posts_joined(db: AsyncSession) -> list[dict]:
    """
    ✅ joinedload: 1 query duy nhất với LEFT JOIN
    """
    stmt = select(Post).options(joinedload(Post.author))
    posts = (await db.scalars(stmt)).unique().all()   # .unique() khi joinedload collection
    return [{"title": p.title, "author": p.author.name} for p in posts]


# Khi nào selectinload vs joinedload?
#
# selectinload (thường dùng):
#   - One-to-many, many-to-many
#   - 2 query nhưng payload không duplicate
#   - Khuyến khích default
#
# joinedload:
#   - Many-to-one (đơn giản, LEFT JOIN sạch)
#   - Khi chỉ cần 1 record related (author của post)
#   - Tránh dùng với collection + pagination → duplicate rows


# ============================================================
# Nested eager loading
# ============================================================

async def get_post_full(db: AsyncSession, post_id: int) -> Post | None:
    """
    Load post + author + comments + comments.author + tags
    Chaining với .options()
    """
    stmt = (
        select(Post)
        .where(Post.id == post_id)
        .options(
            selectinload(Post.author),
            selectinload(Post.comments).selectinload(Comment.author),
            selectinload(Post.tags),
        )
    )
    return await db.scalar(stmt)


# ============================================================
# Filter qua relationship
# ============================================================

async def posts_by_tag(db: AsyncSession, tag_name: str) -> list[Post]:
    """Lấy post có tag tên = tag_name."""
    stmt = (
        select(Post)
        .join(Post.tags)
        .where(Tag.name == tag_name)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return list((await db.scalars(stmt)).all())


# ============================================================
# Aggregate + group by
# ============================================================

async def post_count_per_user(db: AsyncSession) -> list[tuple[str, int]]:
    """Tên user + số post."""
    from sqlalchemy import func
    stmt = (
        select(User.name, func.count(Post.id))
        .outerjoin(Post, Post.author_id == User.id)
        .group_by(User.id, User.name)
        .order_by(func.count(Post.id).desc())
    )
    result = await db.execute(stmt)
    return [(row[0], row[1]) for row in result]


# ============================================================
# Bài tập
# ============================================================
#
# 1. Setup Alembic, migrate 4 bảng trên
#
# 2. Seed data: 3 user, mỗi user 2 post, mỗi post 2-3 tag, 1-2 comment
#
# 3. Viết các query (kèm eager loading):
#    a. Top 5 post mới nhất kèm author name, tag list
#    b. Tất cả comment của user A (bao gồm post.title)
#    c. Tag và số post có tag đó, sắp xếp giảm dần
#    d. Post nào không có comment nào
#    e. User viết post nhiều nhất (1 query, dùng aggregate)
#
# 4. Bật echo=True trong engine, confirm số query mỗi request là HỢP LÝ
#    (list 10 post + eager author + tags → mong đợi 3 query: posts, users, tags)
#
# 5. Xoá 1 user → check posts của user có bị xoá không (cascade)
#
# 6. Pagination 20 post/page có nested comments (mỗi post 1000 comments?)
#    → Cân nhắc: không eager comments trong list, chỉ eager khi GET detail
