"""
Example 03 — Pydantic V2 Sâu

Pydantic V2 (syntax mới) vs V1 - nếu thấy @validator hay class Config là V1, bỏ qua.
Phiên bản hiện tại: pydantic >= 2.0

Chạy standalone: uv run python examples/03_pydantic.py
"""
from datetime import datetime
from enum import Enum
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


# === 1. Model cơ bản + ConfigDict ===
class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,   # auto strip str
        str_to_lower=False,
        extra="forbid",              # không cho field lạ
        frozen=False,                # True → immutable
    )

    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=150)


# Dùng:
u = User(email="a@b.com", name="  An  ", age=25)
print(u.name)  # "An" (stripped)


# === 2. Field với nhiều option ===
class Product(BaseModel):
    name: str = Field(..., description="Tên sản phẩm", examples=["iPhone 15"])
    price: float = Field(gt=0, description="Giá bán (VND)")
    tags: list[str] = Field(default_factory=list, max_length=10)
    stock: int = Field(default=0, ge=0)
    sku: str | None = Field(default=None, pattern=r"^[A-Z]{3}-\d{4}$")


# === 3. field_validator (validate 1 field) ===
class Signup(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password >= 8 ký tự")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password phải có ít nhất 1 số")
        if not any(c.isupper() for c in v):
            raise ValueError("Password phải có ít nhất 1 chữ hoa")
        return v


# === 4. model_validator (validate liên field) ===
class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def check_order(self) -> Self:
        if self.start >= self.end:
            raise ValueError("start phải trước end")
        return self


# === 5. Enum ===
class OrderStatus(str, Enum):
    """Kế thừa str để JSON ra value, không phải 'OrderStatus.NEW'."""

    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"


class Order(BaseModel):
    id: int
    status: OrderStatus = OrderStatus.NEW


# === 6. Nested model ===
class Address(BaseModel):
    street: str
    city: str
    country: str = "VN"


class Customer(BaseModel):
    name: str
    email: EmailStr
    addresses: list[Address] = Field(default_factory=list)


# === 7. Response vs Request model pattern ===
# Common pattern trong FastAPI project:

class UserBase(BaseModel):
    """Field chung."""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Input POST - có password."""
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """Input PATCH - tất cả optional."""
    name: str | None = None
    email: EmailStr | None = None


class UserRead(UserBase):
    """Output - không có password, có id + timestamps."""
    model_config = ConfigDict(from_attributes=True)   # cho phép đọc từ ORM

    id: int
    created_at: datetime


# === 8. Serialize ===
u = User(email="a@b.com", name="An", age=25)
print(u.model_dump())          # dict
print(u.model_dump_json())     # JSON string
print(u.model_dump(exclude={"age"}))   # bỏ field


# === 9. Deserialize ===
raw = '{"email": "x@y.com", "name": "Bob", "age": 30}'
u2 = User.model_validate_json(raw)
print(u2)


# === 10. Computed field ===
from pydantic import computed_field  # noqa: E402


class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height


r = Rectangle(width=3, height=4)
print(r.model_dump())  # {'width': 3.0, 'height': 4.0, 'area': 12.0}


# === Bài tập ===
#
# 1. Tạo model BlogPost:
#    - title (5-200 ký tự)
#    - slug (auto từ title nếu không cung cấp, chỉ chữ/số/dash)
#    - content (min 10 ký tự)
#    - tags (tối đa 5, mỗi tag 2-20 ký tự, lowercase)
#    - published_at (optional datetime, nếu có → phải >= now)
#    Dùng field_validator cho slug, tags. model_validator cho logic phức tạp.
#
# 2. Tạo model BankTransfer:
#    - from_account (str, 10 số)
#    - to_account (str, 10 số)
#    - amount (float, > 0)
#    - @model_validator: from != to
#
# 3. Tạo User -> UserCreate/UserUpdate/UserRead theo pattern đã học
#    Implement password hashing giả:
#    @field_validator("password")
#    → chỉ check strength, KHÔNG hash (hash ở service layer)
