"""
Exercise 01 — Type Hints cơ bản

Python 3.11+ syntax.
Install mypy để check: uv add --dev mypy
Run: mypy 01_type_hints.py
"""
from typing import Any


# --- Bài 1: Primitive types ---
# Thêm type hints cho function sau:
# def greet(name, age, is_admin):
#     return f"{name} ({age}) admin={is_admin}"
# TODO:


# --- Bài 2: Return type ---
# Thêm return type:
# def add(a, b):      # hai int, trả về int
# def divide(a, b):   # hai float, trả về float
# def has_access(user):   # dict, trả về bool
# TODO:


# --- Bài 3: Collections ---
# Thêm type hints:
# - list of str: list[str]
# - dict từ str → int: dict[str, int]
# - list of dict: list[dict[str, Any]]
# Viết function:
# def count_words(texts):     # list[str] → dict[str, int]
#     ...
# TODO:


# --- Bài 4: Optional / None ---
# Python 3.10+: dùng X | None thay cho Optional[X]
# def find_user(email):     # trả về dict hoặc None
#     ...
# TODO:


# --- Bài 5: Union ---
# def parse_id(value):     # nhận int hoặc str, trả về int
#     ...
# Dùng int | str
# TODO:


# --- Bài 6: Callable & function as parameter ---
# from typing import Callable
# def apply(nums, func):    # list[int], function(int)->int, trả về list[int]
#     return [func(n) for n in nums]
# TODO:


# --- Bài 7: TypedDict (mô tả schema dict) ---
# from typing import TypedDict
#
# class UserDict(TypedDict):
#     id: int
#     name: str
#     email: str
#
# def print_user(user: UserDict) -> None:
#     print(user["name"])
# TODO: viết function update_email nhận UserDict và email mới, trả về UserDict mới


# --- Bài 8: Thực hành ---
# Refactor đoạn code dưới với full type hints:
def process_students(students):
    result = {}
    for s in students:
        if s["score"] >= 5:
            result[s["name"]] = "Pass"
        else:
            result[s["name"]] = "Fail"
    return result
# Yêu cầu:
# - students là list của gì? (dùng TypedDict)
# - return là gì?
# TODO: viết lại có type hints


# --- Bài 9: Chạy mypy ---
# Tạo bug cố ý:
# def double(x: int) -> int:
#     return x * "2"   # bug: str thay vì int
# Chạy: mypy 01_type_hints.py
# Quan sát mypy bắt lỗi thế nào
# TODO:
