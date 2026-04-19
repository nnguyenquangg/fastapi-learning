# SQLAlchemy Async 2.0 Cheatsheet

## Engine + Session setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db",
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

## Model declarative

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

## Relationship

```python
# One-to-many
class User(Base):
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

class Post(Base):
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

# Many-to-many
post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
class Post(Base):
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")
```

## Query cơ bản

```python
from sqlalchemy import select

# Lấy 1 theo PK
user = await db.get(User, user_id)

# Select 1
user = await db.scalar(select(User).where(User.email == "a@b.com"))

# Select nhiều
users = list((await db.scalars(select(User))).all())

# Filter + order + limit
stmt = (
    select(User)
    .where(User.is_active == True)
    .order_by(User.created_at.desc())
    .limit(10)
    .offset(20)
)
```

## Relationship loading (tránh N+1)

```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload: 2 query, không dup (khuyến khích default)
stmt = select(Post).options(selectinload(Post.author))

# joinedload: 1 query LEFT JOIN (cho many-to-one nhỏ)
stmt = select(Post).options(joinedload(Post.author))
posts = (await db.scalars(stmt)).unique().all()

# Nested
stmt = select(Post).options(
    selectinload(Post.author),
    selectinload(Post.comments).selectinload(Comment.author),
    selectinload(Post.tags),
)
```

## Aggregate + group

```python
from sqlalchemy import func

# Count
count = await db.scalar(select(func.count(User.id)))

# Count + group
stmt = (
    select(User.role, func.count(User.id))
    .group_by(User.role)
)
rows = (await db.execute(stmt)).all()
```

## Insert, Update, Delete

```python
# Insert (ORM)
user = User(email="a@b.com", name="An")
db.add(user)
await db.flush()       # để có user.id
await db.refresh(user) # lấy default từ DB
await db.commit()

# Update (ORM)
user.name = "New Name"
await db.commit()

# Delete (ORM)
await db.delete(user)
await db.commit()

# Bulk insert (Core, nhanh)
from sqlalchemy import insert
await db.execute(insert(User), [{"email": f"u{i}@x.com", "name": "X"} for i in range(1000)])
await db.commit()

# Bulk update (Core)
from sqlalchemy import update
await db.execute(update(Post).where(Post.is_draft == True).values(is_published=False))
await db.commit()
```

## Transaction

```python
# Auto commit/rollback
async with SessionLocal() as db:
    async with db.begin():
        db.add(user)
        ...   # raise → rollback; thoát OK → commit

# Savepoint
async with db.begin_nested():
    ...
```

## Pagination + total

```python
offset = (page - 1) * size
items = list((await db.scalars(
    select(User).order_by(User.id).offset(offset).limit(size)
)).all())
total = await db.scalar(select(func.count(User.id))) or 0
```

## Filter động

```python
from sqlalchemy import and_, or_

filters = []
if name:
    filters.append(User.name.ilike(f"%{name}%"))
if active is not None:
    filters.append(User.is_active == active)

stmt = select(User)
if filters:
    stmt = stmt.where(and_(*filters))
```

## Raw SQL khi cần

```python
from sqlalchemy import text
result = await db.execute(
    text("SELECT id, name FROM users WHERE email = :email"),
    {"email": "a@b.com"},
)
for row in result:
    print(row.id, row.name)
```

## Common pitfalls

| Lỗi | Giải thích | Fix |
|-----|-----------|-----|
| `MissingGreenlet` | Lazy load trong async | Thêm `selectinload`/`joinedload` |
| Duplicate rows | joinedload với collection | `.unique()` sau scalars |
| `DetachedInstanceError` | Access attribute sau session close | Dùng `expire_on_commit=False` |
| Pool exhausted | Quên close session | Dùng `async with`, không tạo session tay |
| Slow pagination `COUNT(*)` | Table lớn | Dùng cursor-based / estimate |

## Alembic snippet

```bash
# Init
uv run alembic init -t async migrations

# Autogenerate
uv run alembic revision --autogenerate -m "description"

# Apply
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1

# Current version
uv run alembic current
```

## FastAPI tích hợp

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

DbDep = Annotated[AsyncSession, Depends(get_db)]

@app.get("/users/{id}")
async def get_user(id: int, db: DbDep) -> User:
    user = await db.get(User, id)
    if not user:
        raise HTTPException(404)
    return user
```
