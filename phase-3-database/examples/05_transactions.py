"""
Example 05 — Transactions & Unit of Work

Transaction = tập hợp thao tác ACID:
- Atomicity: tất cả hoặc không gì
- Consistency: luôn leave DB ở state hợp lệ
- Isolation: concurrent không đụng nhau
- Durability: commit xong, data bền

Trong async SQLAlchemy:
- Session mặc định đã có 1 transaction ngầm
- commit() = chốt, rollback() = huỷ
- Exception trong session → NÊN rollback
"""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


# ============================================================
# Pattern 1: Transaction đơn (quen thuộc)
# ============================================================
async def transfer_money(db: AsyncSession, from_id: int, to_id: int, amount: Decimal) -> None:
    """Chuyển tiền A → B. Nếu A không đủ → rollback."""
    from_account = await db.get(Account, from_id, with_for_update=True)   # SELECT ... FOR UPDATE
    to_account = await db.get(Account, to_id, with_for_update=True)

    if from_account is None or to_account is None:
        raise ValueError("Account not found")
    if from_account.balance < amount:
        raise InsufficientFundsError("Not enough balance")

    from_account.balance -= amount
    to_account.balance += amount
    await db.commit()
    # Nếu commit lỗi → session tự rollback, exception propagate


# ============================================================
# Pattern 2: Begin nested (savepoint)
# ============================================================
async def bulk_import(db: AsyncSession, records: list[dict]) -> tuple[int, int]:
    """Import nhiều record. Lỗi 1 record không làm hỏng cả batch."""
    success = 0
    failed = 0
    for record in records:
        try:
            async with db.begin_nested():    # tạo SAVEPOINT
                # Code trong block này ở trong nested transaction
                product = Product(name=record["name"], price=record["price"])
                db.add(product)
                # Nếu raise ở đây → chỉ rollback nested, outer vẫn tiếp tục
            success += 1
        except IntegrityError:
            failed += 1
    await db.commit()
    return success, failed


# ============================================================
# Pattern 3: Context manager với session.begin()
# ============================================================
async def place_order(session_factory, user_id: int, items: list[dict]) -> "Order":
    """
    Tự quản lý session + transaction.
    Dùng khi ở ngoài FastAPI dependency (vd: background task, CLI).
    """
    async with session_factory() as db:
        async with db.begin():     # auto commit khi thoát, rollback nếu exception
            user = await db.get(User, user_id)
            if user is None:
                raise ValueError("User not found")

            order = Order(user_id=user_id, status="pending")
            db.add(order)
            await db.flush()       # lấy order.id

            total = Decimal(0)
            for item in items:
                product = await db.get(Product, item["product_id"], with_for_update=True)
                if product.stock < item["quantity"]:
                    raise InsufficientStockError(product.name)
                product.stock -= item["quantity"]
                line = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    unit_price=product.price,
                )
                db.add(line)
                total += product.price * item["quantity"]

            order.total = total
            # thoát with db.begin() → commit
    return order


# ============================================================
# Anti-pattern: commit trong loop
# ============================================================
async def bad_bulk_update(db: AsyncSession, items: list) -> None:
    """❌ Mỗi loop 1 commit → chậm, mất ACID của cả batch."""
    for item in items:
        item.processed = True
        await db.commit()   # ❌ KHÔNG LÀM


async def good_bulk_update(db: AsyncSession, items: list) -> None:
    """✅ Flush nhiều lần nếu cần, commit 1 lần cuối."""
    for item in items:
        item.processed = True
    await db.commit()


# ============================================================
# Bulk operations (nhanh hơn nhiều cho >1000 rows)
# ============================================================
async def bulk_insert_example(db: AsyncSession) -> None:
    """
    session.add_all() OK cho vài trăm rows.
    Với nhiều hơn → dùng Core bulk statement.
    """
    from sqlalchemy import insert
    await db.execute(
        insert(Product),
        [
            {"name": f"Product {i}", "price": 100 + i}
            for i in range(10000)
        ],
    )
    await db.commit()


async def bulk_update_example(db: AsyncSession) -> None:
    from sqlalchemy import update
    await db.execute(
        update(Product).where(Product.stock == 0).values(is_active=False)
    )
    await db.commit()


# ============================================================
# Isolation level (advanced)
# ============================================================
# Default PostgreSQL: READ COMMITTED
# Nâng lên SERIALIZABLE nếu cần tránh phantom read:
#
# engine = create_async_engine(url, isolation_level="SERIALIZABLE")
#
# hoặc theo transaction:
# await db.connection(execution_options={"isolation_level": "SERIALIZABLE"})


# ============================================================
# Concurrency: SELECT FOR UPDATE (pessimistic lock)
# ============================================================
async def decrement_stock(db: AsyncSession, product_id: int, quantity: int) -> None:
    """
    Lock row trong suốt transaction để tránh race condition.
    ⚠ Chỉ dùng khi thực sự cần - có thể gây deadlock nếu lock thứ tự khác nhau
    """
    product = await db.get(Product, product_id, with_for_update=True)
    if product.stock < quantity:
        raise InsufficientStockError(product.name)
    product.stock -= quantity
    await db.commit()


# Hoặc optimistic lock với version column:
# class Product(Base):
#     version: Mapped[int] = mapped_column(default=0)
#     __mapper_args__ = {"version_id_col": version}
# → SQLAlchemy tự check version khi UPDATE, raise StaleDataError nếu bị thay đổi


# ============================================================
# Exception handling đầy đủ
# ============================================================
async def register_user_safe(db: AsyncSession, email: str, name: str) -> "User":
    user = User(email=email, name=name, hashed_password="hashed")
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        # Parse constraint name để biết trùng email hay gì
        if "users_email_key" in str(e.orig):
            raise EmailAlreadyExistsError(email) from e
        raise
    await db.refresh(user)
    return user


# ============================================================
# Placeholders (để example compile)
# ============================================================
class Account: pass
class Product: pass
class User: pass
class Order: pass
class OrderItem: pass
class InsufficientFundsError(Exception): pass
class InsufficientStockError(Exception): pass
class EmailAlreadyExistsError(Exception): pass


# ============================================================
# Bài tập
# ============================================================
#
# 1. Implement `place_order` thật với model thực từ 04_relationships.py
#    - Giảm stock, tạo Order + OrderItem, tính total
#    - Test: chạy 2 request song song mua cùng product - stock không bị âm
#
# 2. Implement `refund_order(order_id)`:
#    - Hoàn lại stock
#    - Đổi status Order
#    - Atomic (rollback nếu bất kỳ bước nào fail)
#
# 3. Benchmark: insert 10000 product bằng 2 cách:
#    - add_all + commit
#    - Core bulk insert
#    So sánh thời gian
#
# 4. Tạo race condition:
#    - 2 terminal, cùng mua 1 product có stock = 1
#    - Version 1 (không for_update): bug - cả 2 đều mua được
#    - Version 2 (for_update): OK - 1 thành công, 1 lỗi
