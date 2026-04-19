"""
Exercise 05 — Errors & Debugging

Try/except, raise, cách đọc traceback.
"""

# --- Bài 1: Đọc traceback ---
# Chạy code dưới đây, đọc lỗi, trả lời:
# 1. Lỗi tên gì?
# 2. Xảy ra ở dòng nào?
# 3. Tại sao lỗi?

# def broken():
#     x = [1, 2, 3]
#     return x[10]
# broken()

# Viết câu trả lời dưới dạng comment:


# --- Bài 2: Try/except cơ bản ---
# Viết function safe_divide(a, b):
# - Nếu b == 0, bắt ZeroDivisionError và trả về None
# - Nếu a hoặc b không phải số, bắt TypeError và trả về None
# - Thành công → trả về a/b
# Test: safe_divide(10, 2), safe_divide(10, 0), safe_divide("a", 2)
# TODO:


# --- Bài 3: Multiple except ---
# Viết function parse_age(s):
# - Input: str
# - Output: int (tuổi)
# - Xử lý:
#   - ValueError (không phải số) → raise ValueError("Tuổi phải là số")
#   - Nếu < 0 hoặc > 150 → raise ValueError("Tuổi không hợp lệ")
# Test: parse_age("25"), parse_age("abc"), parse_age("-5")
# TODO:


# --- Bài 4: Finally ---
# Viết function mở file, đọc nội dung, đóng file
# - Dùng try/finally để đảm bảo file luôn đóng
# - Sau đó viết lại version dùng `with open(...)` — so sánh
# TODO:


# --- Bài 5: Custom exception ---
# Tạo class InsufficientFundsError(Exception)
# Viết function withdraw(balance, amount):
# - Nếu amount > balance → raise InsufficientFundsError
# - Ngược lại → trả về balance - amount
# Catch và in message thân thiện
# TODO:


# --- Bài 6: Debugging với print ---
# Code dưới đây có bug — tìm và fix:
def average(numbers):
    total = 0
    for n in numbers:
        total + n  # bug ở đây?
    return total / len(numbers)

# print(average([10, 20, 30]))   # Kỳ vọng 20.0

# Dùng print để debug từng bước, tìm bug
# TODO: fix


# --- Bài 7: Debugging với pdb (bonus) ---
# Thêm `import pdb; pdb.set_trace()` vào function trên
# Chạy lại, dùng lệnh:
#   n (next), s (step), p <var> (print), c (continue), q (quit)
# Không cần viết code, chỉ thực hành


# --- Bài 8: Validation pattern ---
# Viết function register_user(name, age, email):
# - name: str, không rỗng
# - age: int, 13 <= age <= 120
# - email: str, chứa "@"
# Raise ValueError với message rõ ràng cho mỗi điều kiện
# Nếu OK → trả về dict {name, age, email}
# TODO:
