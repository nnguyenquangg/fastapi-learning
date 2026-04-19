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


# --- Bài 2: TypeVar + Generic ---
# T là placeholder cho "bất kỳ type nào"
# def first(items: list[T]) -> T:
#     return items[0]
# TODO: viết function last(items) trả về phần tử cuối
# Type phải phản ánh được: đưa list[int] → trả int, đưa list[str] → trả str
T = TypeVar("T")
# TODO:


# --- Bài 3: Generic class ---
# Stack đơn giản với generic:
# class Stack(Generic[T]):
#     def __init__(self) -> None:
#         self._items: list[T] = []
#     def push(self, item: T) -> None: ...
#     def pop(self) -> T: ...
# TODO: hoàn thiện class


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


# --- Bài 6: Bài tổng hợp ---
# Viết function paginate:
# - Input: items (list của generic T), page (int), page_size (int)
# - Output: dict có keys: "items" (list T), "page" (int), "total" (int)
# - Dùng TypedDict hoặc Generic
# TODO:
