"""
Exercise 03 — Functions

Viết function, parameter, return, scope.
"""

# --- Bài 1: Basic function ---
# Viết function greet(name) trả về chuỗi "Xin chào, <name>!"
# TODO:


# --- Bài 2: Default argument ---
# Viết function calculate_price(price, discount=0, tax=0.1)
# Trả về: price * (1 - discount) * (1 + tax)
# Test với: calculate_price(100), calculate_price(100, 0.2), calculate_price(100, 0.1, 0.08)
# TODO:


# --- Bài 3: Multiple return ---
# Viết function divide(a, b) trả về (quotient, remainder)
# Nếu b == 0, return (None, None)
# TODO:


# --- Bài 4: *args ---
# Viết function sum_all(*numbers) nhận không giới hạn số, trả về tổng
# Test: sum_all(1, 2, 3), sum_all(1, 2, 3, 4, 5)
# TODO:


# --- Bài 5: **kwargs ---
# Viết function create_user(**info) in ra tất cả thông tin nhận được
# Test: create_user(name="An", age=25, email="an@x.com")
# TODO:


# --- Bài 6: Higher-order function ---
# Viết function apply_to_list(lst, func) áp dụng func lên mỗi phần tử
# Test với lambda: apply_to_list([1,2,3], lambda x: x*2) → [2,4,6]
# TODO:


# --- Bài 7: Recursion ---
# Viết function factorial(n) tính n! bằng đệ quy
# 5! = 5*4*3*2*1 = 120
# TODO:


# --- Bài 8: Scope ---
# Đoán output TRƯỚC khi chạy:
x = 10
def modify():
    x = 20
    print("inside:", x)
modify()
print("outside:", x)
# Viết comment giải thích tại sao

# Sau đó, sửa function để thay đổi được biến x ở scope ngoài
# Gợi ý: global hoặc return
# TODO:


# --- Bài 9: Pure function ---
# Viết 2 function:
# 1. append_item_bad(lst, item) → thêm vào list gốc (có side effect)
# 2. append_item_good(lst, item) → trả về list mới, không thay đổi list gốc
# So sánh output khi gọi 2 lần với cùng input
# TODO:


# --- Bài 10: Docstring ---
# Viết function is_prime(n) kiểm tra n có phải số nguyên tố
# Thêm docstring đầy đủ (mô tả, args, returns, example)
# TODO:
