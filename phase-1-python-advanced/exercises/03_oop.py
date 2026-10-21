"""
Exercise 03 — OOP (ở mức cần cho FastAPI/Pydantic)

Class, init, method, inheritance, property.
"""


# --- Bài 1: Class cơ bản ---
# Tạo class Book:
# - attribute: title (str), author (str), pages (int)
# - method: summary() → trả về "Book: <title> by <author> (<pages> pages)"
# TODO:

class Book():
    def __init__(self, title: str, author: str, pages: int) -> None:
        self.title = title
        self.author = author
        self.pages = pages
        self.rating: int | None = None #Bài 3

    def summary(self) -> str:
        return f"Book: {self.title} by {self.author} ({self.pages} pages)"
    
    #Bài 3
    def is_long(seft) -> bool:
        return seft.pages > 300
    
    def rate(self, score: int) -> None:
        if score < 0 or score > 5:
            raise ValueError("score phải nằm trong khoảng từ 0 đến 5")
        self.rating = score

    #Bài 4
    def __str__(self) -> str:
        return f"Book: {self.title}"
    
    def __repr__(self) -> str: 
        return f"Book(title={self.title}, author={self.author}, pages={self.pages})"

# --- Bài 2: Multiple instances ---
# Tạo 3 instance Book, gọi summary của từng cái
# TODO:

# Tạo 3 instance
book1 = Book("Dế Mèn Phiêu Lưu Ký", "Tô Hoài", 160)
book2 = Book("Truyện Kiều", "Nguyễn Du", 250)
book3 = Book("Python Basics", "An", 300)

# Gọi summary của từng cái
print(book1.summary())
print(book2.summary())
print(book3.summary())

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

class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5 / 9


# --- Bài 6: Inheritance ---
# Tạo:
# - class Animal với name, sound() (base return "...")
# - class Dog(Animal): sound() return "Gâu"
# - class Cat(Animal): sound() return "Meo"
# - Function describe(animals: list[Animal]) in name + sound của từng con
# TODO:

class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def sound(self):
        return "..."
    
class Dog(Animal):
    def sound(self):
        return "Gâu"
    
class Cat(Animal):
    def sound(self):
        return "Meo"
    
def describe(animals: list[Animal]) -> None:
    for animal in animals:
        print(f"{animal.name}: {animal.sound()}")
        

# --- Bài 7: super() ---
# Tạo class User có name, email
# class AdminUser(User) thêm permissions: list[str]
# __init__ của AdminUser phải gọi super().__init__(...)
# TODO:

class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, email={self.email!r})"

class AdminUser(User):
    def __init__(self, name: str, email: str, permissions: list[str]) -> None:
        super().__init__(name, email)
        self.permissions = permissions

    def __repr__(self) -> str:
        return (
            f"AdminUser(name={self.name!r}, email={self.email!r}, "
            f"permissions={self.permissions!r})"
        )


# --- Bài 8: @classmethod và @staticmethod ---
# Tạo class User:
# - __init__(name, email, created_at)
# - @classmethod from_dict(cls, data: dict) → User
# - @staticmethod is_valid_email(email: str) -> bool
# Test:
#   user = User.from_dict({"name": "An", "email": "a@b.com", "created_at": "2025-01-01"})
#   print(User.is_valid_email("a@b.com"))
# TODO:

class User:
    def __init__(self, name: str, email: str, created_at: str) -> None:
        self.name = name
        self.email = email
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict) -> User:
        return cls(
            name = data["name"],
            email = data["email"],
            created_at = data["created_at"]
        )
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    def __repr__(self) -> str:
        return (
            f"User(name={self.name!r}, email={self.email!r}, "
            f"created_at={self.created_at!r})"
        )

# --- Bài 9: Composition (có > kế thừa) ---
# Tạo:
# - # --- Bài 9: Composition (có > kế thừa) ---
# Tạo:
# - class Address(street, city)
# - class User(name, address: Address)
# - Method full_address() → "name — street, city"
# TODO:(street, city)
# - class User(name, address: Address)
# - Method full_address() → "name — street, city"
# TODO:

class Address:
    def __init__(self, street: str, city: str):
        self.street = street
        self.city = city

class User:
    def __init__(self, name: str, address: Address):
        self.name = name
        self.address = address

    def full_address(self) -> str:
        return f"{self.name} - {self.address.street}, {self.address.city}"

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

class UserModel:
    def __init__(self, email: str, age: int):
        if "@" not in email:
            raise ValueError("Invalid email")
        if age < 0 or age > 150:
            raise ValueError("Invalid age")
        self.email = email
        self.age = age

# --Test--

# Test đúng
test = UserModel("phuc@gmail.com", 26)
print(test.email, test.age)

# Test email sai
# testEmail = UserModel("phuc.gmail.com", 26)
# print(testEmail.email, testEmail.age)

# Test age sai
# testAge = UserModel("phuc@gmail.com", -1)
# print(testAge.email, testAge.age)
# Test age sai
# testAge = UserModel("phuc@gmail.com", 200)
# print(testAge.email, testAge.age)