"""
Exercise 04 — Dataclass và Enum

Dataclass giảm boilerplate. Enum để đại diện tập giá trị cố định.
Cả hai đều dùng nhiều trong FastAPI.
"""
from dataclasses import dataclass, field, FrozenInstanceError
from enum import Enum


# --- Bài 1: Dataclass cơ bản ---
# Viết lại class Book của bài 03 bằng @dataclass:
# @dataclass
# class Book:
#     title: str
#     author: str
#     pages: int
# Test:
#   b = Book("Clean Code", "Robert Martin", 464)
#   print(b)           # auto __repr__
#   print(b == Book("Clean Code", "Robert Martin", 464))  # auto __eq__
# TODO:


# --- Bài 2: Default value ---
@dataclass
class Product:
    name: str
    price: float
    tags: list[str] = field(default_factory=list)   # ⚠ KHÔNG dùng tags: list[str] = []
    in_stock: bool = True
#
# Tại sao dùng default_factory? → vì mutable default sẽ share giữa các instance
# TODO: tạo 2 Product, thử thêm tag vào 1 cái, xem cái kia có bị ảnh hưởng không

test1 = Product("Áo thun", 150000)
test2 = Product("Quần jean", 400000)

test1.tags.append("sale")
print(test1)
print(test2)
print(test2.tags)  # [] -> p2 không bị ảnh hưởng


# --- Bài 3: frozen=True (immutable) ---
# @dataclass(frozen=True)
# class Point:
#     x: float
#     y: float
#
# p = Point(1, 2)
# p.x = 3   # Error! frozen dataclass không sửa được
#
# Vì sao dùng? → hashable (có thể dùng làm key của dict/set), an toàn hơn
# TODO: tạo Point, thử gán lại x, quan sát lỗi

@dataclass(frozen=True)
class Point:
    x: float
    y: float

point = Point(1,2)
print(point)

# Gán lại x
try:
    point.x = 5
except FrozenInstanceError as e:
    print("Lỗi:", e)

print(point.x) # x vẫn không đổi

# --- Bài 4: __post_init__ ---
# Muốn validate sau khi khởi tạo, dùng __post_init__
@dataclass
class User:
    email: str
    age: int

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email")
        if self.age < 0:
            raise ValueError("Age must be >= 0")
# TODO: test với input sai

test = User("phuc@gmail.com", 26)
print(test)

# Email sai
try:
    User("an.gmail.com", 25)
except ValueError as e:
    print("Lỗi:", e)

# Tuổi sai
try:
    User("an@gmail.com", -5)
except ValueError as e:
    print("Lỗi:", e)

# Trường hợp sai cả 2 lỗi thì báo lỗi gặp đầu tên
try:
    User("abc", -1)
except ValueError as e:
    print("Lỗi:", e)


# --- Bài 5: Enum ---
# from enum import Enum
# class Priority(Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"
#
# Dùng như:
#   p = Priority.HIGH
#   print(p.name)    # "HIGH"
#   print(p.value)   # "high"
#   p == Priority.HIGH   # True
# TODO: tạo enum Status có PENDING, ACTIVE, COMPLETED, CANCELLED

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

status = Status.ACTIVE
print(status)
print(status.name)
print(status.value)


# --- Bài 6: Dataclass + Enum ---
# @dataclass
# class Task:
#     title: str
#     priority: Priority = Priority.MEDIUM
#     status: Status = Status.PENDING
# Viết function filter_tasks(tasks, status) trả về list task có status đó
# TODO:

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    title: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING

def filter_tasks(tasks, status):
    result = []
    for task in tasks:
        if task.status == status:
            result.append(task)
    return result

# --- Test ---
tasks = [
    Task("Viết báo cáo", Priority.HIGH, Status.ACTIVE),
    Task("Học Python"),
    Task("Dọn bàn làm việc", Priority.LOW, Status.COMPLETED),
    Task("Gọi điện cho khách", Priority.HIGH, Status.PENDING),
    Task("Đặt vé máy bay", status=Status.CANCELLED),
]

pending_tasks = filter_tasks(tasks, Status.PENDING)

for task in pending_tasks:
    print(task.title)


# --- Bài 7: IntEnum ---
# IntEnum dùng khi cần so sánh số
from enum import IntEnum
class Level(IntEnum):
    GUEST = 0
    USER = 1
    ADMIN = 2
#
# Level.ADMIN > Level.USER  # True
# TODO: viết function can_delete(role: Level) → True nếu role >= ADMIN

def can_delete(role: Level) -> bool:
    return role >= Level.ADMIN

print(can_delete(Level.USER))
print(can_delete(Level.ADMIN))


# --- Bài 8: Bài tổng hợp ---
# Mô hình một hệ thống đơn hàng:
# - Enum OrderStatus: NEW, PAID, SHIPPED, DELIVERED, CANCELLED
# - Dataclass OrderItem: product_name, price, quantity
#   - property total → price * quantity
# - Dataclass Order: id, items: list[OrderItem], status: OrderStatus = NEW
#   - property total → tổng từ items
#   - method mark_paid() → chuyển status, raise nếu không ở NEW
# TODO:

class OrderStatus(Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass
class OrderItem:
    product_name: str
    price: str 
    quantity: int

    @property
    def total(self) -> float:
        return self.price * self.quantity
    
@dataclass
class Order:
    id: int
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.NEW

    @property
    def total(self) -> float:
        result = 0
        for item in self.items:
            result += item.total
        return result
    
    def mark_paid(self) -> None:
        if self.status != OrderStatus.NEW:
            raise ValueError(f"Chỉ đơn NEW mới thanh toán được, đơn hiện tại: {self.status.name}")
        self.status = OrderStatus.PAID

# --- Test ---
order = Order(
    id=1,
    items=[
        OrderItem("Áo thun", 150000, 2),
        OrderItem("Quần jean", 400000, 1),
    ],
)

print(order.items[0].total)
print(order.total)
print(order.status)

order.mark_paid()
print(order.status) # sau khi gọi order.mark_paid() thì status đã được chuyển thành PAID

# Thanh toán lần 2
try:
    order.mark_paid()
except ValueError as e:
    print("Lỗi:", e)