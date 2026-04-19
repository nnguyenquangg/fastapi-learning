"""
Exercise 04 — Dataclass và Enum

Dataclass giảm boilerplate. Enum để đại diện tập giá trị cố định.
Cả hai đều dùng nhiều trong FastAPI.
"""
from dataclasses import dataclass, field
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
# @dataclass
# class Product:
#     name: str
#     price: float
#     tags: list[str] = field(default_factory=list)   # ⚠ KHÔNG dùng tags: list[str] = []
#     in_stock: bool = True
#
# Tại sao dùng default_factory? → vì mutable default sẽ share giữa các instance
# TODO: tạo 2 Product, thử thêm tag vào 1 cái, xem cái kia có bị ảnh hưởng không


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


# --- Bài 4: __post_init__ ---
# Muốn validate sau khi khởi tạo, dùng __post_init__
# @dataclass
# class User:
#     email: str
#     age: int
#
#     def __post_init__(self) -> None:
#         if "@" not in self.email:
#             raise ValueError("Invalid email")
#         if self.age < 0:
#             raise ValueError("Age must be >= 0")
# TODO: test với input sai


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


# --- Bài 6: Dataclass + Enum ---
# @dataclass
# class Task:
#     title: str
#     priority: Priority = Priority.MEDIUM
#     status: Status = Status.PENDING
# Viết function filter_tasks(tasks, status) trả về list task có status đó
# TODO:


# --- Bài 7: IntEnum ---
# IntEnum dùng khi cần so sánh số
# from enum import IntEnum
# class Level(IntEnum):
#     GUEST = 0
#     USER = 1
#     ADMIN = 2
#
# Level.ADMIN > Level.USER  # True
# TODO: viết function can_delete(role: Level) → True nếu role >= ADMIN


# --- Bài 8: Bài tổng hợp ---
# Mô hình một hệ thống đơn hàng:
# - Enum OrderStatus: NEW, PAID, SHIPPED, DELIVERED, CANCELLED
# - Dataclass OrderItem: product_name, price, quantity
#   - property total → price * quantity
# - Dataclass Order: id, items: list[OrderItem], status: OrderStatus = NEW
#   - property total → tổng từ items
#   - method mark_paid() → chuyển status, raise nếu không ở NEW
# TODO:
