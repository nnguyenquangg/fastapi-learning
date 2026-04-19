"""
Example 01 — pytest cơ bản

Chạy:
    uv run pytest examples/01_pytest_basics.py -v
"""
import pytest


# ============================================================
# 1. Test đơn giản
# ============================================================
def add(a: int, b: int) -> int:
    return a + b


def test_add():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-1, 1) == 0


# ============================================================
# 2. pytest.raises (test exception)
# ============================================================
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Can't divide by zero")
    return a / b


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Can't divide"):
        divide(10, 0)


def test_divide_ok():
    assert divide(10, 2) == 5.0


# ============================================================
# 3. Parametrize (1 test, nhiều input)
# ============================================================
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 3, 5),
        (-1, 1, 0),
        (0, 0, 0),
        (100, 200, 300),
    ],
)
def test_add_parametrized(a: int, b: int, expected: int):
    assert add(a, b) == expected


# Với id cho dễ đọc:
@pytest.mark.parametrize(
    "email,is_valid",
    [
        ("a@b.com", True),
        ("invalid", False),
        ("@b.com", False),
        ("a@", False),
    ],
    ids=["valid", "no-at", "no-local", "no-domain"],
)
def test_email_validation(email: str, is_valid: bool):
    result = "@" in email and email.index("@") not in (0, len(email) - 1)
    assert result == is_valid


# ============================================================
# 4. Fixture
# ============================================================
@pytest.fixture
def sample_user() -> dict:
    """Tạo data mẫu dùng cho nhiều test."""
    return {"id": 1, "email": "a@b.com", "name": "An"}


def test_user_name(sample_user: dict):
    assert sample_user["name"] == "An"


def test_user_email(sample_user: dict):
    assert "@" in sample_user["email"]


# Fixture trả về hàm (parametrized factory):
@pytest.fixture
def make_user():
    def _make(name: str = "Default", age: int = 25) -> dict:
        return {"name": name, "age": age}
    return _make


def test_make_user_default(make_user):
    u = make_user()
    assert u["name"] == "Default"


def test_make_user_custom(make_user):
    u = make_user(name="Bob", age=30)
    assert u == {"name": "Bob", "age": 30}


# ============================================================
# 5. Fixture scope
# ============================================================
# Default scope = "function" (tạo lại cho mỗi test)
# Scopes: "function" | "class" | "module" | "package" | "session"

@pytest.fixture(scope="module")
def expensive_resource():
    """Tạo 1 lần cho cả module (vd: DB connection)."""
    print("\n[setup] creating expensive resource")
    resource = {"connection": "open"}
    yield resource
    print("\n[teardown] closing resource")
    resource["connection"] = "closed"


def test_use_resource(expensive_resource):
    assert expensive_resource["connection"] == "open"


# ============================================================
# 6. Markers
# ============================================================
@pytest.mark.slow
def test_slow_thing():
    import time
    time.sleep(0.1)   # giả lập slow
    assert True


# Chạy: pytest -m slow   → chỉ chạy test có mark slow
# Skip: pytest -m "not slow"


# ============================================================
# 7. Skip / xfail
# ============================================================
@pytest.mark.skip(reason="Feature chưa làm")
def test_future_feature():
    assert False


@pytest.mark.skipif(True, reason="Chỉ chạy trên Linux")
def test_linux_only():
    ...


@pytest.mark.xfail(reason="Known bug, sẽ fix sau")
def test_known_bug():
    assert 1 == 2


# ============================================================
# 8. AAA pattern (Arrange - Act - Assert)
# ============================================================
class Calculator:
    def __init__(self) -> None:
        self._history: list[str] = []

    def add(self, a: int, b: int) -> int:
        result = a + b
        self._history.append(f"{a}+{b}={result}")
        return result

    @property
    def history(self) -> list[str]:
        return self._history.copy()


def test_calculator_records_history():
    # Arrange
    calc = Calculator()

    # Act
    calc.add(2, 3)
    calc.add(10, 20)

    # Assert
    assert calc.history == ["2+3=5", "10+20=30"]


# ============================================================
# Bài tập
# ============================================================
#
# 1. Viết function is_prime(n) và test:
#    - parametrize với [1, 2, 3, 4, 5, 10, 13, 100]
#    - edge case: n = 0, n = -1 (raise ValueError)
#
# 2. Implement class ShoppingCart:
#    - add_item(name, price, quantity)
#    - remove_item(name)
#    - total() -> float
#    - is_empty -> bool
#    Viết test cho mỗi method, dùng fixture cho cart sẵn có 3 item
#
# 3. Viết test cho email validator (trong bài 3):
#    - Nhiều input valid/invalid
#    - Dùng parametrize với ids
#    - Đảm bảo có test cho edge case: "", " ", "a@b.c", None
