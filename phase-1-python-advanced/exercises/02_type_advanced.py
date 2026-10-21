"""
Exercise 02 — Type Hints nâng cao (Generic, Literal, Annotated)

Các type hint FastAPI và Pydantic hay dùng.
"""
from typing import Annotated, Generic, Literal, TypeVar


# --- Bài 1: Literal ---
# Literal cho phép hạn chế giá trị cố định
# def set_level(level: Literal["low", "medium", "high"]) -> None:
#     print(f"Level: {level}")
# set_level("low")       # OK
# set_level("xxx")       # mypy sẽ báo lỗi
# TODO: viết function set_role chỉ nhận "admin" | "user" | "guest"

def set_role(role: Literal["admin", "user", "guest"]) -> None:
    print(f"Role: {role}")

set_role("admin")
set_role("user")
set_role("boss")     # mypy báo lỗi

# --- Bài 2: TypeVar + Generic ---
# T là placeholder cho "bất kỳ type nào"
# def first(items: list[T]) -> T:
#     return items[0]
# TODO: viết function last(items) trả về phần tử cuối
# Type phải phản ánh được: đưa list[int] → trả int, đưa list[str] → trả str
T = TypeVar("T")
# TODO:
def first(items: list[T]) -> T:
    return items[0]

def last(items: list[T]) -> T:
    return items[-1]


# --- Bài 3: Generic class ---
# Stack đơn giản với generic:
# class Stack(Generic[T]):
#     def __init__(self) -> None:
#         self._items: list[T] = []
#     def push(self, item: T) -> None: ...
#     def pop(self) -> T: ...
# TODO: hoàn thiện class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None: 
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()


# --- Bài 4: Annotated (quan trọng cho FastAPI!) ---
# Annotated gắn metadata vào type mà runtime có thể đọc được
# from typing import Annotated
#
# UserId = Annotated[int, "primary key, positive"]
# def get_user(id: UserId) -> dict: ...
#
# FastAPI dùng Annotated để gắn Depends, Query, Path...
# Ví dụ thật trong FastAPI (xem qua, không chạy):
# from fastapi import Query
# async def list_items(
#     limit: Annotated[int, Query(gt=0, le=100)] = 10,
# ): ...
# TODO: chỉ cần đọc hiểu, không có bài tập riêng


# --- Bài 5: Protocol (duck typing với type hint) ---
# from typing import Protocol
#
# class Drawable(Protocol):
#     def draw(self) -> None: ...
#
# def render(item: Drawable) -> None:
#     item.draw()
#
# # Bất kỳ class nào có method draw() đều dùng được
# class Circle:
#     def draw(self) -> None: print("○")
#
# class Square:
#     def draw(self) -> None: print("□")
#
# render(Circle())  # OK
# render(Square())  # OK

# TODO: viết Protocol Serializable có method to_json() -> str
# Tạo class User có to_json, verify mypy OK
import json
from typing import Protocol

class Serializable(Protocol):
    def to_json(self) -> str: ...

def save(item: Serializable) -> None:
    print("Đã lưu:", item.to_json())

class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
    
    def to_json(self) -> str:
        return json.dumps({"name": self.name, "age": self.age})
    
class Product:
    def __init__(self, title: str, price: int) -> None:
        self.title = title
        self.price = price
    
    def to_json(self) -> str:
        return json.dumps({"title": self.title, "price": self.price}, ensure_ascii=False)
    
class Cat:
    pass

save(User("An", 20))          # OK
save(Product("Bút", 5000.0))  # OK
# save(Cat())                   # mypy báo lỗi

# --- Bài 6: Bài tổng hợp ---
# Viết function paginate:
# - Input: items (list của generic T), page (int), page_size (int)
# - Output: dict có keys: "items" (list T), "page" (int), "total" (int)
# - Dùng TypedDict hoặc Generic
# TODO:

T = TypeVar("T")

class Page(Generic[T]):
    def __init__(self, items: list[T], page: int, total: int) -> None:
        self.items = items
        self.page = page
        self.total = total

    def to_dict(self) -> dict[str, object]:
        return {"items": self.items, "page": self.page, "total": self.total}

def paginate(items: list[T], page: int, page_size: int) -> Page[T]:
    if page < 1 or page_size < 1:
        raise ValueError("page và page_size phải >= 1")
    
    start = (page - 1) * page_size
    end = start + page_size
    return Page(items[start:end], page, len(items))