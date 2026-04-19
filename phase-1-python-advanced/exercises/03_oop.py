"""
Exercise 03 — OOP (ở mức cần cho FastAPI/Pydantic)

Class, init, method, inheritance, property.
"""


# --- Bài 1: Class cơ bản ---
# Tạo class Book:
# - attribute: title (str), author (str), pages (int)
# - method: summary() → trả về "Book: <title> by <author> (<pages> pages)"
# TODO:


# --- Bài 2: Multiple instances ---
# Tạo 3 instance Book, gọi summary của từng cái
# TODO:


# --- Bài 3: Method với logic ---
# Thêm vào class Book:
# - is_long(): bool, True nếu pages > 300
# - rate(score: int): gán self.rating = score (0-5), invalid → raise ValueError
# TODO:


# --- Bài 4: __str__ vs __repr__ ---
# Thêm:
# - __str__: "Book: <title>"
# - __repr__: "Book(title='...', author='...', pages=...)"
# Test: print(book), repr(book)
# TODO:


# --- Bài 5: @property ---
# Tạo class Temperature:
# - khởi tạo với celsius
# - property fahrenheit: tính từ celsius
# - setter fahrenheit: set lại celsius tương ứng
# Test:
#   t = Temperature(celsius=0)
#   print(t.fahrenheit)  # 32
#   t.fahrenheit = 100
#   print(t.celsius)     # ~37.78
# TODO:


# --- Bài 6: Inheritance ---
# Tạo:
# - class Animal với name, sound() (base return "...")
# - class Dog(Animal): sound() return "Gâu"
# - class Cat(Animal): sound() return "Meo"
# - Function describe(animals: list[Animal]) in name + sound của từng con
# TODO:


# --- Bài 7: super() ---
# Tạo class User có name, email
# class AdminUser(User) thêm permissions: list[str]
# __init__ của AdminUser phải gọi super().__init__(...)
# TODO:


# --- Bài 8: @classmethod và @staticmethod ---
# Tạo class User:
# - __init__(name, email, created_at)
# - @classmethod from_dict(cls, data: dict) → User
# - @staticmethod is_valid_email(email: str) -> bool
# Test:
#   user = User.from_dict({"name": "An", "email": "a@b.com", "created_at": "2025-01-01"})
#   print(User.is_valid_email("a@b.com"))
# TODO:


# --- Bài 9: Composition (có > kế thừa) ---
# Tạo:
# - class Address(street, city)
# - class User(name, address: Address)
# - Method full_address() → "name — street, city"
# TODO:


# --- Bài 10: Class mô phỏng Pydantic (preview) ---
# Pydantic cho validation tự động, nhưng mình mô phỏng bằng tay:
# class UserModel:
#     def __init__(self, email: str, age: int):
#         if "@" not in email:
#             raise ValueError("Invalid email")
#         if age < 0 or age > 150:
#             raise ValueError("Invalid age")
#         self.email = email
#         self.age = age
# TODO: viết UserModel + test với input đúng/sai
#       Note: Phase 2 Pydantic sẽ làm việc này tự động & sạch hơn
