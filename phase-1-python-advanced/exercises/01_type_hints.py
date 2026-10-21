"""
Exercise 01 — Type Hints cơ bản

Python 3.11+ syntax.
Install mypy để check: uv add --dev mypy
Run: mypy 01_type_hints.py
"""
from typing import Any
# def add(a: int, b: int) -> int:
#     return a + b

# result = add(10, "20")


# --- Bài 1: Primitive types ---
# Thêm type hints cho function sau:
# def greet(name, age, is_admin):
#     return f"{name} ({age}) admin={is_admin}"
# TODO:
def greet(name: str, age: int, is_admin: bool) -> str:
    return f"{name} ({age}) admin={is_admin}"
print(greet("Phúc", 25, True))

# --- Bài 2: Return type ---
# Thêm return type:
# def add(a, b):      # hai int, trả về int
# def divide(a, b):   # hai float, trả về float
# def has_access(user):   # dict, trả về bool
# TODO:
def add(a: int, b: int) -> int:
    return a + b

def divide(a: float, b: float) -> float:
    return a / b

def has_access(user: dict) -> bool:
    return user["id"]

# --- Bài 3: Collections ---
# Thêm type hints:
# - list of str: list[str]
# - dict từ str → int: dict[str, int]
# - list of dict: list[dict[str, Any]]
# Viết function:
# def count_words(texts):     # list[str] → dict[str, int]
#     ...
# TODO:
texts = ["hello", "python", "hello", "fastapi", "python"]
def count_words(texts: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}

    for text in texts:
        result[text] = result.get(text, 0) + 1

    return result

print(count_words(texts))


# --- Bài 4: Optional / None ---
# Python 3.10+: dùng X | None thay cho Optional[X]
# def find_user(email):     # trả về dict hoặc None
#     ...
# TODO:
def find_user(email: str)-> dict | None:
    users = {
        "phuc@gmail.com": {"name": "Phuc", "age": 26},
        "jame@gmail.com": {"name": "Jame", "age": 30}
    } 
    return users.get(email)

user = find_user("phuc@gmail.com")
if user is not None:
    print(user["name"])
else:
    print("Không tìm thấy user")


# --- Bài 5: Union ---
# def parse_id(value):     # nhận int hoặc str, trả về int
#     ...
# Dùng int | str
# TODO:

def parse_id(value: int | str) -> int:
    if isinstance(value, int):
        return value
    return int(value.strip())

print(parse_id(21))


# --- Bài 6: Callable & function as parameter ---
# from typing import Callable
# def apply(nums, func):    # list[int], function(int)->int, trả về list[int]
#     return [func(n) for n in nums]
# TODO:
from collections.abc import Callable
def apply(nums: list[int], func: Callable[[int], int]) -> list[int]:
    return [func(n) for n in nums]

def double(n: int) -> int:
    return n * 2

numbers = [1,2,3,4,5]

result = apply(numbers, double)
print(result)


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
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: str

def print_user(user: UserDict) -> None:
    print(user["name"])

def update_email(user: UserDict, new_email: str) -> UserDict:
    update_user = user.copy()
    update_user["email"] = new_email
    return update_user

user: UserDict = {
    "id": 1,
    "name": "Phúc",
    "email": "phuc@gmail.com",
}

print_user(user)
updated_user = update_email(user, "newemail@gmail.com")

print(updated_user)
print(user)


# --- Bài 8: Thực hành ---
# Refactor đoạn code dưới với full type hints:
# def process_students(students):
#     result = {}
#     for s in students:
#         if s["score"] >= 5:
#             result[s["name"]] = "Pass"
#         else:
#             result[s["name"]] = "Fail"
#     return result
# Yêu cầu:
# - students là list của gì? (dùng TypedDict): Là danh sách học sinh, mỗi học sinh là một dict có name và score. Khai báo bằng TypedDict
# - return là gì?: Là một dict cho biết mỗi học sinh đậu hay rớt, vd: {"Phuc": "Pass", "Long": "Fail"}
# TODO: viết lại có type hints
from typing import Literal

class Student(TypedDict):
    name: str
    score: float

Status = Literal["Pass", "Fail"]

def process_students(students: list[Student]) -> dict[str, Status]:
    result: dict[str, Status] = {}
    for s in students:
        if s["score"] >= 5:
            result[s["name"]] = "Pass"
        else:
            result[s["name"]] = "Fail"
    return result


# --- Bài 9: Chạy mypy ---
# Tạo bug cố ý:
# def double(x: int) -> int:
#     return x * "2"   # bug: str thay vì int
# Chạy: mypy 01_type_hints.py
# Quan sát mypy bắt lỗi thế nào
# TODO:
# 01_type_hints.py:185: error: Incompatible return value type (got "str", expected "int")  [return-value]
# Found 1 error in 1 file (checked 1 source file)
# - 01_type_hints.py:2 -> lỗi ở dòng 2
# - got "str" -> hàm đang được trả về chuỗi
# - expected "int" -> nhưng đã khai báo int, tức là phải trả về số nguyên
# - [return-value] -> tên lỗi
